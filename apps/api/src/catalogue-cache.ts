import type { Catalogue } from '@ohm-sweet-ohm/domain';

export interface CatalogueSource {
  loadCatalogue(): Promise<Catalogue>;
  catalogueVersion(): Promise<string>;
}

export interface CatalogueCacheOptions {
  /** Minimum time between two version checks; the site lags an import by at most this. */
  readonly checkIntervalMs: number;
  readonly now: () => number;
  readonly onCheckFailed: (error: unknown) => void;
}

/**
 * Keeps the catalogue in memory and reloads it only after an import (decision in PROJECT_LOG,
 * 2026-10-14): the version is checked at most once per interval, and when the check or the
 * reload fails, the catalogue already in memory keeps being served until the next check.
 */
export class CatalogueCache {
  private catalogue: Catalogue | undefined;
  private version: string | undefined;
  private lastCheck = Number.NEGATIVE_INFINITY;
  private refreshing: Promise<Catalogue> | undefined;

  constructor(
    private readonly source: CatalogueSource,
    private readonly options: CatalogueCacheOptions,
  ) {}

  /** The current catalogue; only the very first load can fail. */
  async get(): Promise<Catalogue> {
    if (
      this.catalogue !== undefined &&
      this.options.now() - this.lastCheck < this.options.checkIntervalMs
    ) {
      return this.catalogue;
    }
    // Concurrent requests share one refresh instead of each querying the database.
    this.refreshing ??= this.refresh().finally(() => {
      this.refreshing = undefined;
    });
    return this.refreshing;
  }

  private async refresh(): Promise<Catalogue> {
    const cached = this.catalogue;
    try {
      const version = await this.source.catalogueVersion();
      const catalogue =
        cached !== undefined && version === this.version
          ? cached
          : await this.source.loadCatalogue();
      this.catalogue = catalogue;
      this.version = version;
      this.lastCheck = this.options.now();
      return catalogue;
    } catch (error) {
      if (cached === undefined) throw error;
      this.options.onCheckFailed(error);
      this.lastCheck = this.options.now();
      return cached;
    }
  }
}

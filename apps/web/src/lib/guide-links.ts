import { posix } from 'node:path';

/** Repository folder holding the guides; the content collections read the same folder. */
export const GUIDES_DIR = 'troubleshooting';

/** Route of the troubleshooting menu; each guide lives under it at `/<folder>`. */
export const GUIDES_ROUTE = '/depannage';

/**
 * Where the repository files a guide links to (template, licence) are browsed: `main` on purpose,
 * the site is deployed from it.
 */
const REPOSITORY_TREE = `https://github.com/benoit-bremaud/ohm-sweet-ohm/blob/main/${GUIDES_DIR}`;

const SCHEME = /^[a-z][a-z\d+.-]*:/i;

/**
 * Maps a link written for GitHub in a guide to its web target. `fromDir` is the folder of the
 * Markdown file relative to `troubleshooting/` (`''` for the menu). A guide README becomes its
 * route, the menu becomes the index, any other repository file goes to GitHub; absolute URLs,
 * anchors and figures (resolved by Astro next to the guide) are left alone.
 *
 * @throws if the target leaves `troubleshooting/`, which fails the build.
 */
export function rewriteGuideHref(href: string, fromDir: string): string {
  if (href === '' || href.startsWith('#') || href.startsWith('/') || SCHEME.test(href)) {
    return href;
  }
  const hashAt = href.search(/[?#]/);
  const path = hashAt === -1 ? href : href.slice(0, hashAt);
  const hash = hashAt === -1 ? '' : href.slice(hashAt);
  if (/\.svg$/i.test(path)) return href;

  const target = posix.normalize(posix.join(fromDir, path));
  if (target.startsWith('..')) {
    throw new Error(`guide link ${href} in ${fromDir || 'README.md'} leaves troubleshooting/`);
  }
  if (target === 'README.md') return `${GUIDES_ROUTE}${hash}`;
  const folder = /^([^/]+)\/README\.md$/.exec(target)?.[1];
  if (folder !== undefined) return `${GUIDES_ROUTE}/${folder}${hash}`;
  return `${REPOSITORY_TREE}/${target}${hash}`;
}

interface HastNode {
  type: string;
  tagName?: string;
  properties?: Record<string, unknown>;
  children?: HastNode[];
}

interface VFileLike {
  path?: string;
}

/**
 * Folder of `filePath` relative to the `troubleshooting/` directory, `''` for its root, `undefined`
 * for a file outside it.
 */
export function guideDir(filePath: string): string | undefined {
  const parts = filePath.split(/[\\/]/);
  const at = parts.lastIndexOf(GUIDES_DIR);
  if (at === -1) return undefined;
  return parts.slice(at + 1, -1).join('/');
}

/** Rehype plugin: rewrites the links of every Markdown file under `troubleshooting/`. */
export function rehypeGuideLinks() {
  return (tree: HastNode, file: VFileLike) => {
    const fromDir = file.path === undefined ? undefined : guideDir(file.path);
    if (fromDir === undefined) return;
    const visit = (node: HastNode) => {
      const href = node.properties?.href;
      if (node.tagName === 'a' && typeof href === 'string') {
        node.properties = { ...node.properties, href: rewriteGuideHref(href, fromDir) };
      }
      node.children?.forEach(visit);
    };
    visit(tree);
  };
}

import { posix } from 'node:path';

/** Route of the troubleshooting menu; each guide lives under it at `/<folder>`. */
export const GUIDES_ROUTE = '/depannage';

/** Where the repository files a guide links to (template, licence) are browsed. */
const REPOSITORY_TREE = 'https://github.com/benoit-bremaud/ohm-sweet-ohm/blob/main/troubleshooting';

const SCHEME = /^[a-z][a-z\d+.-]*:/i;

/**
 * Maps a link written for GitHub in a guide to its web target. `fromDir` is the folder of the
 * Markdown file relative to `troubleshooting/` (`''` for the menu). A guide README becomes its
 * route, the menu becomes the index, any other repository file goes to GitHub; absolute URLs,
 * anchors and figures are left alone.
 */
export function rewriteGuideHref(href: string, fromDir: string): string {
  if (href === '' || href.startsWith('#') || href.startsWith('/') || SCHEME.test(href)) {
    return href;
  }
  const hashAt = href.indexOf('#');
  const path = hashAt === -1 ? href : href.slice(0, hashAt);
  const hash = hashAt === -1 ? '' : href.slice(hashAt);
  if (path.endsWith('.svg')) return href;

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

/** Folder of `filePath` relative to the `troubleshooting/` directory, `''` for its root. */
export function guideDir(filePath: string): string {
  const parts = filePath.split(/[\\/]/);
  const at = parts.lastIndexOf('troubleshooting');
  if (at === -1) return '';
  return parts.slice(at + 1, -1).join('/');
}

/** Rehype plugin: rewrites the links of every Markdown file under `troubleshooting/`. */
export function rehypeGuideLinks() {
  return (tree: HastNode, file: VFileLike) => {
    if (file.path === undefined || !/[\\/]troubleshooting[\\/]/.test(file.path)) return;
    const fromDir = guideDir(file.path);
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

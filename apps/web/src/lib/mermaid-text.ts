import { flowchartSteps } from './flowchart-text';
import { treeFile } from './mermaid-trees';

interface MdastNode {
  type: string;
  lang?: string | null;
  value?: string;
  url?: string;
  alt?: string;
  children?: MdastNode[];
}

/** Alt of every diagram image (decision trees and block diagrams alike); its text follows it. */
export const DIAGRAM_ALT = "Schéma ; sa version texte suit l'image.";

const escapeHtml = (text: string) =>
  text
    .replaceAll(/&/g, '&amp;')
    .replaceAll(/</g, '&lt;')
    .replaceAll(/>/g, '&gt;')
    .replaceAll(/"/g, '&quot;');

/** The diagram as an ordered list of steps, each with its branches, folded under a summary. */
export function diagramText(source: string): string {
  const steps = flowchartSteps(source).map((step) => {
    const branches = step.branches.map((b) => {
      const arrow = b.condition === undefined ? `→ ${b.to}` : `${b.condition} → ${b.to}`;
      return `<li>${escapeHtml(arrow)}</li>`;
    });
    const nested = branches.length === 0 ? '' : `<ul>${branches.join('')}</ul>`;
    return `<li>${escapeHtml(step.label)}${nested}</li>`;
  });
  return `<details><summary>Version texte du schéma</summary><ol>${steps.join('')}</ol></details>`;
}

/**
 * Remark plugin: replaces Mermaid block n of a guide by the image `arbre-n.svg` that `just trees`
 * rendered next to it, followed by its text version. GitHub still draws the block from the
 * Markdown; the site never runs a browser.
 */
export function remarkMermaidImages() {
  // `unknown`, narrowed below: the mdast types are not a dependency of the site.
  return (tree: unknown) => {
    let index = 0;
    const visit = (node: MdastNode) => {
      if (node.children === undefined) return;
      node.children = node.children.flatMap((child) => {
        if (child.type !== 'code' || child.lang !== 'mermaid') {
          visit(child);
          return [child];
        }
        const image = { type: 'image', url: treeFile(index), alt: DIAGRAM_ALT };
        index += 1;
        return [
          { type: 'paragraph', children: [image] },
          { type: 'html', value: diagramText(child.value ?? '') },
        ];
      });
    };
    if (isNode(tree)) visit(tree);
  };
}

function isNode(value: unknown): value is MdastNode {
  return typeof value === 'object' && value !== null && 'type' in value;
}

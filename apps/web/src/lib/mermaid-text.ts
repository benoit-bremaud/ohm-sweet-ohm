import { flowchartSteps } from './flowchart-text';

/** The few hast fields the plugin reads or writes. */
interface HastNode {
  type: string;
  tagName?: string;
  properties?: Record<string, unknown>;
  children?: HastNode[];
  value?: string;
}

/** Text alternative of every tree image; the full tree follows it in text. */
export const TREE_ALT = "Arbre de décision ; sa version texte suit l'image.";

const text = (value: string): HastNode => ({ type: 'text', value });
const el = (tagName: string, children: HastNode[]): HastNode => ({
  type: 'element',
  tagName,
  properties: {},
  children,
});

const mermaidCode = (node: HastNode): HastNode | undefined => {
  if (node.tagName !== 'pre') return undefined;
  const code = node.children?.find((c) => c.type === 'element');
  const classes = code?.properties?.className;
  return Array.isArray(classes) && classes.includes('language-mermaid') ? code : undefined;
};

const sourceOf = (code: HastNode) => (code.children ?? []).map((c) => c.value ?? '').join('');

/** The tree as an ordered list of steps, each with its branches, folded under a summary. */
export function treeText(source: string): HastNode {
  const steps = flowchartSteps(source).map((step) =>
    el('li', [
      text(step.label),
      ...(step.branches.length === 0
        ? []
        : [
            el(
              'ul',
              step.branches.map((b) =>
                el('li', [
                  text(b.condition === undefined ? `→ ${b.to}` : `${b.condition} → ${b.to}`),
                ]),
              ),
            ),
          ]),
    ]),
  );
  return el('details', [el('summary', [text("Version texte de l'arbre")]), el('ol', steps)]);
}

/**
 * Rehype plugin, to run before rehype-mermaid: gives each Mermaid tree an `accDescr` (it becomes
 * the image's alt) and a text version after it, so the tree reads without the picture.
 */
export function rehypeMermaidText() {
  return (tree: HastNode) => {
    const visit = (node: HastNode) => {
      const children = node.children;
      if (children === undefined) return;
      for (let i = 0; i < children.length; i += 1) {
        const child = children[i];
        if (child === undefined) continue;
        const code = mermaidCode(child);
        if (code === undefined) {
          visit(child);
          continue;
        }
        const source = sourceOf(code);
        const [head = '', ...rest] = source.split('\n');
        code.children = [text([head, `  accDescr: ${TREE_ALT}`, ...rest].join('\n'))];
        children.splice(i + 1, 0, treeText(source));
        i += 1;
      }
    };
    visit(tree);
  };
}

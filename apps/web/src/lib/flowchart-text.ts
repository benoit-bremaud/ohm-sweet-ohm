/** A step of a decision tree and the branches that leave it, labels in reading order. */
export interface FlowStep {
  label: string;
  branches: { condition: string | undefined; to: string }[];
}

const NODE = String.raw`([A-Za-z0-9_]+)\s*(?:\[([^\]]*)\]|\{([^}]*)\}|\(([^)]*)\))?`;
// `A --> B`, `A -- oui --> B`, `A -.-> B`, `A -. texte .-> B`, each end with an optional label.
const EDGE = new RegExp(
  `^\\s*${NODE}\\s*(?:--\\s*(.+?)\\s*-->|-->|-\\.\\s*(.+?)\\s*\\.->|-\\.->)\\s*${NODE}\\s*$`,
);
const LONE_NODE = new RegExp(`^\\s*${NODE}\\s*$`);

const clean = (label: string) =>
  label
    .replace(/<br\s*\/?>/gi, ' ')
    .replace(/^"|"$/g, '')
    .replace(/\s+/g, ' ')
    .trim();

/**
 * Reads the steps of a Mermaid flowchart, for a text version of the tree beside its image.
 * Steps keep the order in which the source first names them; a node never labelled shows its id.
 * One link or one node per line, links written `-->`, `-- text -->`, `-.->` or `-. text .->`;
 * any other link syntax throws, so a guide cannot lose a branch silently.
 */
export function flowchartSteps(source: string): FlowStep[] {
  const labels = new Map<string, string>();
  const order: string[] = [];
  const edges: { from: string; condition: string | undefined; to: string }[] = [];

  const name = (id: string, ...label: (string | undefined)[]) => {
    if (!order.includes(id)) order.push(id);
    const text = label.find((l) => l !== undefined);
    if (text !== undefined) labels.set(id, clean(text));
  };

  for (const line of source.split('\n')) {
    const edge = EDGE.exec(line);
    if (edge !== null) {
      const [, from = '', f1, f2, f3, cond, dotted, to = '', t1, t2, t3] = edge;
      name(from, f1, f2, f3);
      name(to, t1, t2, t3);
      const condition = cond ?? dotted;
      edges.push({ from, condition: condition && clean(condition), to });
      continue;
    }
    // A bare word is a directive (`end`, the header's tail): only a bracketed line declares a node.
    const lone = LONE_NODE.exec(line);
    if (lone !== null && /[[{(]/.test(line)) {
      const [, id = '', l1, l2, l3] = lone;
      name(id, l1, l2, l3);
      continue;
    }
    // Any other link syntax would vanish from the text version: stop the build instead.
    if (/--|==|-\./.test(line)) {
      throw new Error(
        `Mermaid link not understood, the text version would drop it: ${line.trim()}`,
      );
    }
  }

  const label = (id: string) => labels.get(id) ?? id;
  return order.map((id) => ({
    label: label(id),
    branches: edges
      .filter((e) => e.from === id)
      .map((e) => ({ condition: e.condition, to: label(e.to) })),
  }));
}

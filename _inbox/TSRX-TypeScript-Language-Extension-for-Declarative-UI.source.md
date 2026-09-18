---
source_url: https://tsrx.dev/blog/removing-lazy-destructuring
fetched_at: 2026-09-18T14:45:39Z
fetch_method: jina
issue: 333
cover_image: https://tsrx.dev/images/tsrx-mark.svg?v=3
title_zh: 去掉 Lazy Destructuring
tech_domain: frontend
---

# TSRX | TypeScript Language Extension for Declarative UI

September 14, 2026

## Removing lazy destructuring

TSRX no longer has`&{ ... }`and`&[ ... ]`. Destructuring is ordinary destructuring again, and reactive state is read through your framework's own API.

Since the beginning, TSRX has carried one extension to the ECMAScript binding grammar: a pattern prefixed with`&`that looked like destructuring but deferred every property or index access until the binding was read. Each reference compiled back to a member expression on a hidden source object.

```
1 const UserCard = (&{ name, age }: { name: string; age: number }) => <div>
2   <h2>{name}</h2>
3   <p>Age: {age}</p>
4 </div>;
5 
6 let &[count, setCount] = createSignal(0);
```

As of today's release it is gone from the language. Writing`&`before`{`or`[`in a binding position is a syntax error, exactly as it is in TypeScript. There is no replacement syntax. The full reasoning is in[RFC #106](https://github.com/tsrx-org/tsrx/discussions/106); this post is the short version.

## Why it existed

Lazy destructuring was built for Ripple. Ripple props used to be objects with accessor properties, so a plain`{ name }`would read the accessor once and snapshot the value, breaking per-access reactivity across the component boundary. The`&`kept the ergonomics of destructuring while compiling every read back to`props.name`. The same trick was then applied to`track()`so a bare`count`could read and write a tracked value.

Ripple has since made props plain objects. Reactivity crosses the component boundary explicitly, as a`Tracked`or`Derived`that the child reads through`.value`. With prop getters gone, the only remaining use was sugar over`track()`, and no other target ever needed the feature: React, Preact, and Octane re-run the component body on every render, Solid's own guidance is to read`props.name`rather than destructure, and Vue's reactive proxy already makes`state.count`reactive on its own.

## What was wrong with it

One pattern produced two different kinds of binding, and nothing at the use site told you which one you were holding.

```
1 let &[count, countT] = track(0);
2 
3 countT.value++; // the tracked object
4 count++;        // secretly the same write, spelled like a local
```

Hovering`count`in an editor showed`number`. The type checker, and every tool built on it, believed it was a plain value. To make the declaration type-check at all, Ripple's`Tracked<V>`had to claim it was also a`[V, Tracked<V>]`tuple, and the compiler then needed two dedicated errors to stop people from indexing it. Reactivity was invisible in the type system exactly where it mattered most.

A lazy binding was also not a variable, and JavaScript treats bindings as values in places you might not think about.

```
1 function Profile(&{ name }: Props) @{
2   // Reads as "copy a local into an object".
3   // Compiled to { name: __lazy0.name }: a property read from props.
4   const snapshot = { name };
5 
6   <p>{snapshot.name}</p>
7 }
```

The same applied to`val++`, which mutated someone else's array. Each case was handled correctly by the compiler; the cost fell on the reader, who had to remember that an`&`many lines above changed the meaning of every later occurrence of the name.

Finally, the syntax was whitespace sensitive and not TypeScript.`&{`introduced a pattern only when the bracket followed the ampersand directly;`& {`did not. Every tool in the chain had to reproduce that rule: the parser, Prettier, ESLint, the TextMate and Tree-sitter grammars, the editor queries, the language server's source mappings, and the OXC and Yuku ports. Most TSRX code is now written or edited by language models, whose prior is TypeScript plus the target framework's own idioms. A model that forgot the`&`produced code that compiled and rendered once, silently. One explicit way to read reactive state, spelled the way the framework's own docs spell it, is the safer design.

## What to write instead

Each target's own state API is the replacement. For React, Preact, and Octane, the output for a former lazy parameter is the plain destructure you would have written anyway.

```
1 function UserCard({ name, age }: { name: string; age: number }) @{
2   <div>
3     <h2>{name}</h2>
4     <p>Age: {age}</p>
5   </div>
6 }
```

For Solid, read props through the props object, or use`splitProps`when you want to pull some of them apart. This is the idiom Solid's own tooling recommends.

```
1 function UserCard(props: { name: string; age: number }) @{
2   <div>
3     <h2>{props.name}</h2>
4     <p>Age: {props.age}</p>
5   </div>
6 }
```

For Vue, read through the reactive proxy, or use`toRefs`when destructuring is what you want.

```
1 function Counter() @{
2   const state = reactive({ count: 0 });
3 
4   <button onClick={() => state.count++}>{state.count}</button>
5 }
```

For Ripple, hold the tracked object and read and write`.value`. Passing`count`to a child passes the tracked object; passing`count.value`passes a number. The two spellings look different because they are different.

```
1 export function Counter() @{
2   const count = track(0);
3 
4   <button onClick={() => count.value++}>{count.value}</button>
5   <Child {count} />
6 }
```

## Migrating

The rewrites are mechanical. A file that still uses the sigils fails to compile with a syntax error pointing at the`&`, so nothing changes meaning silently.

```
1 // Ripple
 2 let &[count] = track(0); count++;        →  const count = track(0); count.value++;
 3 let &[c, cT] = track(0); <Child count={cT} />  →  const count = track(0); <Child {count} />
 4 function Card({ count: &[count] }: P)    →  function Card({ count }: P) and count.value
 5 
 6 // Solid
 7 (&{ name }: Props) => <p>{name}</p>      →  (props: Props) => <p>{props.name}</p>
 8 
 9 // Vue
10 let &{ count } = state                   →  state.count, or toRefs(state)
11 
12 // React, Preact, Octane
13 (&{ name }: Props)                       →  ({ name }: Props)
```

Alongside the language change, the`tsrx/no-lazy-destructuring-in-modules`ESLint rule is removed since it has nothing left to check, Prettier no longer prints the prefix, and the editor grammars no longer highlight it. The`Tracked<V>`types in Ripple become honest`{ value: V }`shapes in Ripple's next release, which also drops the tracked-index errors.

## What this means for TSRX

This is the last of the early TSRX-only ideas that predated the current design. The language now adds statement containers, marked control flow, scoped styles, and submodules on top of TypeScript and JSX, and nothing else. Every binding is a TypeScript binding; every destructure is a TypeScript destructure. That is a smaller language to learn, a smaller language for tools to implement, and a language that matches what people and models already expect.

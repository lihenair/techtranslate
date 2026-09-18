---
source_url: https://shift.infinite.red/legend-state-the-fastest-react-state-library-youre-probably-not-using-e791171a61b7
fetched_at: 2026-09-18T14:45:43Z
fetch_method: jina
issue: 333
title_zh: Legend State：你可能没用过的最快 React 状态库
tech_domain: frontend
---

# Legend State: The Fastest React State Library You’re Probably Not Using

[![Image 1: Darin Wilson](https://miro.medium.com/v2/resize:fill:64:64/2*KfmHGbSEdINCFdBr5YHbrA.jpeg)](https://medium.com/@darinw?source=post_page---byline--e791171a61b7-----------------------------------------)

6 min read

3 days ago

Press enter or click to view image in full size

![Image 2: Illustration of a smart phone, with surrounding iconography suggesting speed and high-performance](https://miro.medium.com/v2/resize:fit:700/1*alpsLPNIv6sbKesURpcYaA.png)

Jay Meistrich is on a mission.

He’s determined to get your React Native apps as fast as they can possibly be.

He first did this by creating Legend List, a super-optimized list component that [boasts performance levels that rival even the venerable FlashList](https://github.com/LegendApp/legend-list#legend-list).

But that wasn’t enough.

At [his recent talk at Chain React 2026](https://www.youtube.com/watch?v=qcnqSldXZ08), he explained that after working with multiple companies helping them improve performance, he realized that lists weren’t the biggest problem. It was something much more subtle.

It was state.

As it turned out, React’s built-in state support (`useState`, `useContext`) was often the source of serious performance problems.

The solution? As Jay said in his talk: “just use a state library”. There are many to choose from, and most will be an improvement over what ships with React.

But, Jay being Jay, he went out and built his own: [Legend State](https://legendstate.com/), now in beta for version 3.0. In his talk, he discussed the problem with React state, and gave an impressive demo of how Legend State solves it.

### The Problem with useState

> “The key to building the fastest apps is to minimize the amount of work that React and React Native do. That means having smaller renders, and rendering less often. `useState` and `useContext` are just fundamentally incompatible with that goal.” — Jay Meistrich

The problem with useState is that it both creates _and_ subscribes to state.

That sounds innocuous enough, but consider this example from Jay’s slides:

function ChatScreen() {  
 const [replyId, setReplyId] = useState('')
return (  
 <View>  
 <ChatMessages replyId={replyId} />  
 <ChatComposer replyId={replyId} />  
 </View>  
 )  
}

function ChatMessage({ id, replyId }) {  
 const isReply = id === replyId

}

`ChatScreen` creates the `replyId` value, then passes it down to its children. But it’s now also **subscribed** to `replyId`. This means that it, and all its children, will have to re-render every time `replyId` changes, even though `ChatScreen` itself does nothing with `replyId` beyond passing the value.

`ChatScreen` doesn’t need to re-render when `replyId` changes; only the children that care about it need to re-render. But `ChatScreen` is forced to re-render regardless.

Compiler and memoizing can’t help, because the value is actually changing, and that forces the re-render.

`useContext` can sometimes help, but as Jay says “instead of going deep, it goes wide”. Every consumer of a context re-renders when any value inside it changes, whether or not the consumer uses the part that changed.

You can try to get around that by creating smaller, more-focused providers, but then you quickly end up with this all-too-familiar pattern:

function App() {  
 return (  
 <SomeProvider>  
 <SomeOtherProvider>  
 <YetAnotherProvider>  
 <ThisWillBeTheLastOneProvider>  
 <OkJustOneMoreProvider>  
 <FinalFinalProvider>  
 <SendHelpProvider>  
 <ActualApp />  
 </SendHelpProvider>  
 </FinalFinalProvider>  
 </OkJustOneMoreProvider>  
 </ThisWillBeTheLastOneProvider>  
 </YetAnotherProvider>  
 </SomeOtherProvider>  
 </SomeProvider>  
 )  
}
### How Serious Of a Problem Is This Really?

Potentially quite serious.

Jay ran a benchmark with three different implementations of a timer for a music app that updates four times a second.

In the first example, `useState` is called at the app root. In the second, it’s called in the middle of the tree, and in the third, in the leaf component:

  
function App() {  
 const [time, setTime] = useState(0)
return (  
 <Window>  
 <PlaybackArea time={time} />  
 <Playlist />  
 <BottomToolbar />  
 </Window>  
 )  
}

function PlaybackArea() {  
 const [time, setTime] = useState(0)

return (  
 <View>  
 <PlaybackTime time={time} />  
 <TheRestOfThePlaybackArea />  
 </View>  
 )  
}

function ElapsedText() {  
 const [time, setTime] = useState(0)

return (  
 <Text>{time}</Text>  
 )  
}

In his benchmark, the “app root” version ran **10 times slower** than the “leaf text” version. So state is definitely something to consider when you’re thinking about performance.

### What Makes Legend State Different?

To illustrate the difference, Jay showed a different example of a music app where the background color of a track in a playlist changes when it becomes the currently-playing track.

Here’s one solution that uses `useState`:

function MusicApp() {  
 const [playback, setPlayback] = useState(initialPlayback);
return <TrackList activeTrackId={playback.activeTrackId} />;  
}

function TrackList({ activeTrackId }) {  
 return tracks.map((track) => (  
 <TrackRowWrapper  
 key={track.id}  
 track={track}  
 activeTrackId={activeTrackId}  
 />  
 ));  
}

function TrackRowWrapper({ track, activeTrackId }) {  
 const isActive = activeTrackId === track.id;

return <TrackRowView track={track} isActive={isActive} />;  
}

This example tries to mitigate the problem by computing the `isActive` boolean in the wrapper and passing that down instead. Assuming `TrackRowView` is memoized , the rows whose `isActive` didn’t change can then skip the render.

## Get Darin Wilson’s stories in your inbox

Join Medium for free to get updates from this writer.

Remember me for faster sign in

This helps, but there’s no avoiding that whenever `setPlayback` is called, `MusicApp` re-renders, `TrackList` re-renders, and so do all of the wrapper components in the list, even though all we really need to do is re-render two `TrackRowView` components: the one representing the previously-playing track, and the new one.

So how does Legend State handle this?

The fix Jay lands on is that **_state shouldn’t live in React at all_**.

In Legend State you create an `observable` (he notes some people call these “signals”), and the crucial difference is that **creating state and subscribing to it are two separate operations**:

  
const playback$ = observable({  
 tracks: [],  
 activeTrackId: null,  
});
function TrackRow({ track }) {  
 const isActive = useValue(  
   
 () => playback$.activeTrackId.get() === track.id,  
 );

return (  
 <View style={[styles.row, isActive && styles.activeRow]}>  
 <Text>{track.title}</Text>  
 </View>  
 );  
}

That `$` suffix is just a naming convention meaning “this is an observable”. There’s no magic attached to it.

The observable (`playback$` in this case) is stable. The nodes within it can be mutated by calling `set()` or `assign()`, but the observable itself does not change.

`useValue` is how we get notified when something in an observable changes, and consumers can subscribe to the specific parts of the observable that they care about:

const isActive = useValue(  
 () => playback$.activeTrackId.get() === track.id,  
 );

The passed-in function runs once at first, and the `get()` call subscribes us to future changes to `playback$.activeTrackId`.

When `activeTrackId` changes, the function is run again and `isActive` changes when the return value of the function changes. Only then does a re-render happen.

Consider a 500-track playlist. When `activeTrackId` changes, all 500 selector functions re-run, but each one is a single string comparison, executed outside of React. For 498 of them the result is unchanged, so React is never notified and no render is scheduled.

Only two components need to re-render: the old track and the new track, and nothing else. Legend State makes sure that’s exactly what happens.

### Going Even More Fine-Grained

Then Jay pushes further, and this is where, by his own admission, things get strange.

In the previous example, when a track becomes active, a single background color changes, but the whole `TrackRow` re-renders to make that happen. And sometimes, even that is more than you want.

To solve this, Legend State ships reactive versions of the built-in components, prefixed with `$`, that accept reactive props:

function TrackRow({ track }) {  
 return (  
 <$View  
 $style={() => [  
 styles.row,  
 playback$.activeTrackId.get() === track.id && styles.activeRow,  
 ]}  
 />  
 );  
}
Now `TrackRow` renders once, on mount, and never again.

When `activeTrackId` changes, only the `$style` function re-runs, inside a tiny wrapper component that Legend State inserts for you. Your component’s body doesn’t execute.

This approach changes the idea of what a component actually is. With this usage, it’s something that sets up the structure once but then never fully re-renders. Only smaller pieces within the component update themselves as specific pieces of data change over time.

Jay himself admits that the syntax of the high-performance features of Legend State “may look alien and very scary”, but it’s important to remember that the standard usage we saw in the last section is the default behavior, and it’s plenty fast.

But when you’ve got a hot-path component that needs more optimization, Legend State has options to help get you there.

### Going Further

Beyond just performance, Legend State’s architecture enables a host of other features, which Jay touched on at the end of his talk:

*   `useObserveEffect` is a replacement for `useEffect` that’s triggered by state updates, not renders. This makes your code easier to reason about, and gets rid of confusing and possibly performance-killing dependency arrays.
*   State changes carry not only the new value, but also the old value and the path into the state object where the change occurred. This enabled the addition of an undo/redo feature (added by Infinite Red’s own Jamon Holmgren!).
*   The detailed state changes also enabled the addition of a full offline-first sync engine, with your choice of backend. This is included in the library, with plugins for common backends, and very little code needed to set it up. But this, as Jay says, “is a whole other talk”.

Jay goes into a lot more detail, so definitely check out the full talk below to get the big picture of what Legend State can do.

You may, like me, decide that Legend State will be a serious contender the next time you’re reaching for a state library.

<!-- media:youtube id="qcnqSldXZ08" url="https://www.youtube.com/watch?v=qcnqSldXZ08" -->

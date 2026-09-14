---
source_url: https://transformer-circuits.pub/2021/framework/index.html
fetched_at: 2026-09-14T02:29:16Z
fetch_method: jina
issue: 312
title_zh: Transformer 电路的数学框架
tech_domain: ai
---

# A Mathematical Framework for Transformer Circuits

### Contents

*   [Model Simplifications](https://transformer-circuits.pub/2021/framework/index.html#model-simplifications)
*   [High-Level Architecture](https://transformer-circuits.pub/2021/framework/index.html#high-level-architecture)
*   [Virtual Weights and the Residual Stream as a Communication Channel](https://transformer-circuits.pub/2021/framework/index.html#residual-comms)
*   [Attention Heads are Independent and Additive](https://transformer-circuits.pub/2021/framework/index.html#architecture-attn-independent)
*   [Attention Heads as Information Movement](https://transformer-circuits.pub/2021/framework/index.html#architecture-attn-as-movement)

*   [The Path Expansion Trick](https://transformer-circuits.pub/2021/framework/index.html#onel-path-expansion)
*   [Splitting Attention Head terms into Query-Key and Output-Value Circuits](https://transformer-circuits.pub/2021/framework/index.html#splitting-attention-head-terms-into-circuits)
*   [Interpretation as Skip-Trigrams](https://transformer-circuits.pub/2021/framework/index.html#interpretation-as-skip-trigrams)
*   [Summarizing OV/QK Matrices](https://transformer-circuits.pub/2021/framework/index.html#summarizing-ovqk-matrices)
*   [Do We "Fully Understand" One-Layer Models?](https://transformer-circuits.pub/2021/framework/index.html#do-we-fully-understand-one-layer-models)

*   [Three Kinds of Composition](https://transformer-circuits.pub/2021/framework/index.html#three-kinds-of-composition)
*   [Path Expansion of Logits](https://transformer-circuits.pub/2021/framework/index.html#path-expansion-of-logits)
*   [Path Expansion of Attention Scores QK Circuit](https://transformer-circuits.pub/2021/framework/index.html#path-expansion-of-attention-scores-qk-circuit)
*   [Analyzing a Two-Layer Model](https://transformer-circuits.pub/2021/framework/index.html#analyzing-a-two-layer-model)
*   [Induction Heads](https://transformer-circuits.pub/2021/framework/index.html#induction-heads)
*   [Term Importance Analysis](https://transformer-circuits.pub/2021/framework/index.html#term-importance-analysis)
*   [Virtual Attention Heads](https://transformer-circuits.pub/2021/framework/index.html#virtual-attention-heads)

Transformer language models are an emerging technology that is gaining increasingly broad real-world use, for example in systems like GPT-3 , LaMDA , Codex , Meena , Gopher , and similar models. However, as these models scale, their open-endedness and high capacity creates an increasing scope for unexpected and sometimes harmful behaviors. Even years after a large model is trained, both creators and users routinely discover model capabilities – including problematic behaviors – they were previously unaware of.

One avenue for addressing these issues is mechanistic interpretability, attempting to reverse engineer the detailed computations performed by transformers, similar to how a programmer might try to reverse engineer complicated binaries into human-readable source code. If this were possible, it could potentially provide a more systematic approach to explaining current safety problems, identifying new ones, and perhaps even anticipating the safety problems of powerful future models that have not yet been built. A previous project, the [Distill Circuits thread](https://distill.pub/2020/circuits/), has attempted to reverse engineer vision models, but so far there hasn’t been a comparable project for transformers or language models.

In this paper, we attempt to take initial, very preliminary steps towards reverse-engineering transformers. Given the incredible complexity and size of modern language models, we have found it most fruitful to start with the simplest possible models and work our way up from there. Our aim is to discover simple algorithmic patterns, motifs, or frameworks that can subsequently be applied to larger and more complex models. Specifically, in this paper we will study transformers with two layers or less which have only attention blocks – this is in contrast to a large, modern transformer like GPT-3, which has 96 layers and alternates attention blocks with MLP blocks.

We find that by conceptualizing the operation of transformers in a new but mathematically equivalent way, we are able to make sense of these small models and gain significant understanding of how they operate internally. Of particular note, we find that specific attention heads that we term “induction heads” can explain in-context learning in these small models, and that these heads only develop in models with at least two attention layers. We also go through some examples of these heads operating in action on specific data.

We don’t attempt to apply to our insights to larger models in this first paper, but in a [forthcoming paper](https://transformer-circuits.pub/2022/in-context-learning-and-induction-heads/index.html), we will show that both our mathematical framework for understanding transformers, and the concept of induction heads, continues to be at least partially relevant for much larger and more realistic models – though we remain a very long way from being able to fully reverse engineer such models.

* * *

## Summary of Results

#### Reverse Engineering Results

To explore the challenge of reverse engineering transformers, we reverse engineer several toy, attention-only models. In doing so we find:

*   Zero layer transformers model bigram statistics.The bigram table can be accessed directly from the weights.
*   One layer attention-only transformers are an ensemble of bigram and “skip-trigram” (sequences of the form "A… B C") models.The bigram and skip-trigram tables can be accessed directly from the weights, without running the model. These skip-trigrams can be surprisingly expressive. This includes implementing a kind of very simple in-context learning.
*   Two layer attention-only transformers can implement much more complex algorithms using compositions of attention heads. These compositional algorithms can also be detected directly from the weights. Notably, two layer models use attention head composition to create “induction heads”, a very general in-context learning algorithm.We’ll explore induction heads in much more detail in a forthcoming paper.
*   One layer and two layer attention-only transformers use very different algorithms to perform in-context learning.Two layer attention heads use qualitatively more sophisticated inference-time algorithms — in particular, a special type of attention head we call an induction head — to perform in-context-learning, forming an important transition point that will be relevant for larger models.

#### Conceptual Take-Aways

We’ve found that many subtle details of the transformer architecture require us to approach reverse engineering it in a pretty different way from how the InceptionV1 Circuits work . We’ll unpack each of these points in the sections below, but for now we briefly summarize. We’ll also expand on a lot of the terminology we introduce here once we get to the appropriate sections. (To be clear, we don't intend to claim that any of these points are necessarily novel; many are implicitly or explicitly present in other papers.)

*   Attention heads can be understood as independent operations, each outputting a result which is added into the residual stream.Attention heads are often described in an alternate “concatenate and multiply” formulation for computational efficiency, but this is mathematically equivalent.
*   Attention-only models can be written as a sum of interpretable end-to-end functions mapping tokens to changes in logits.These functions correspond to “paths” through the model, and are linear if one freezes the attention patterns.
*   Transformers have an enormous amount of linear structure.One can learn a lot simply by breaking apart sums and multiplying together chains of matrices.
*   Attention heads can be understood as having two largely independent computations: a QK (“query-key”) circuit which computes the attention pattern, and an OV (“output-value”) circuit which computes how each token affects the output if attended to.
*   Key, query, and value vectors can be thought of as intermediate results in the computation of the low-rank matrices W_Q^TW_K and W_OW_V. It can be useful to describe transformers without reference to them.
*   Composition of attention heads greatly increases the expressivity of transformers. There are three different ways attention heads can compose, corresponding to keys, queries, and values. Key and query composition are very different from value composition.
*   All components of a transformer (the token embedding, attention heads, MLP layers, and unembedding) communicate with each other by reading and writing to different subspaces of the residual stream. Rather than analyze the residual stream vectors, it can be helpful to decompose the residual stream into all these different communication channels, corresponding to paths through the model.

* * *

## Transformer Overview

Before we attempt to reverse engineer transformers, it's helpful to briefly review the high-level structure of transformers and describe how we think about them.

In many cases, we've found it helpful to reframe transformers in equivalent, but non-standard ways. Mechanistic interpretability requires us to break models down into human-interpretable pieces. An important first step is finding the representation which makes it easiest to reason about the model. In modern deep learning, there is —for good reason! —a lot of emphasis on computational efficiency, and our mathematical descriptions of models often mirror decisions in how one would write efficient code to run the model. But when there are many equivalent ways to represent the same computation, it is likely that the most human-interpretable representation and the most computationally efficient representation will be different.

Reviewing transformers will also let us align on terminology, which can sometimes vary. We'll also introduce some notation in the process, but since this notation is used across many sections, we provide a detailed description of all notation in the [notation appendix](https://transformer-circuits.pub/2021/framework/index.html#notation) as a concise reference for readers.

### Model Simplifications

To demonstrate the ideas in this paper in their cleanest form, we focus on "toy transformers" with some simplifications.

In most parts of this paper, we will make a very substantive change: we focus on “attention-only” transformers, which don't have MLP layers. This is a very dramatic simplification of the transformer architecture. We're partly motivated by the fact that circuits with attention heads present new challenges not faced by the Distill circuits work, and considering them in isolation allows us to give an especially elegant treatment of those issues. But we've also simply had much less success in understanding MLP layers so far; in normal transformers with both attention and MLP layers there are many circuits mediated primarily by attention heads which we can study, some of which seem very important, but the MLP portions have been much harder to get traction on. This is a major weakness of our work that we plan to focus on addressing in the future. Despite this, we will have some discussion of transformers with MLP layers in later sections.

We also make several changes that we consider to be more superficial and are mostly made for clarity and simplicity. We do not consider biases, but a model with biases can always be simulated without them by folding them into the weights and creating a dimension that is always one. Additionally, biases in attention-only transformers mostly multiply out to functionally be biases on the logits. We also ignore layer normalization. It adds a fair amount of complexity to consider explicitly, and up to a variable scaling, layer norm can be merged into adjacent weights. We also expect that, modulo some implementational annoyances, layer norm could be substituted for batch normalization (which can fully be folded into adjacent parameters).

### High-Level Architecture

There are several variants of transformer language models. We focus on autoregressive, decoder-only transformer language models, such as GPT-3. (The original transformer paper had a special encoder-decoder structure to support translation, but many modern language models don't include this.)

A transformer starts with a token embedding, followed by a series of “residual blocks”, and finally a token unembedding. Each residual block consists of an attention layer, followed by an MLP layer. Both the attention and MLP layers each “read” their input from the residual stream (by performing a linear projection), and then “write” their result to the residual stream by adding a linear projection back in.Each attention layer consists of multiple heads, which operate in parallel.

![Image 1](blob:http://localhost/2abf4fa8197fdfc85bc2fe79f4c5d804)
### Virtual Weights and the Residual Stream as a Communication Channel

One of the main features of the high level architecture of a transformer is that each layer adds its results into what we call the “residual stream.”Constructing models with a residual stream traces back to early work by the Schmidhuber group, such as highway networks and LSTMs, which have found significant modern success in the more recent residual network architecture . In transformers, the residual stream vectors are often called the “embedding.” We prefer the residual stream terminology, both because it emphasizes the residual nature (which we believe to be important) and also because we believe the residual stream often dedicates subspaces to tokens other than the present token, breaking the intuitions the embedding terminology suggests. The residual stream is simply the sum of the output of all the previous layers and the original embedding. We generally think of the residual stream as a communication channel, since it doesn't do any processing itself and all layers communicate through it.

![Image 2](blob:http://localhost/35ced6528a8bb717dda8c6dc3d37b7cc)
The residual stream has a deeply linear structure.It's worth noting that the completely linear residual stream is very unusual among neural network architectures: even ResNets , the most similar architecture in widespread use, have non-linear activation functions on their residual stream, or applied whenever the residual stream is accessed! Every layer performs an arbitrary linear transformation to "read in" information from the residual stream at the start,This ignores the layer normalization at the start of each layer, but up to a constant scalar, the layer normalization is a constant affine transformation and can be folded into the linear transformation. See discussion of how we handle layer normalization in the appendix. and performs another arbitrary linear transformation before adding to "write" its output back into the residual stream. This linear, additive structure of the residual stream has a lot of important implications. One basic consequence is that the residual stream doesn't have a ["privileged basis"](https://transformer-circuits.pub/2021/framework/index.html#def-privileged-basis); we could rotate it by rotating all the matrices interacting with it, without changing model behavior.

#### Virtual Weights

An especially useful consequence of the residual stream being linear is that one can think of implicit "virtual weights" directly connecting any pair of layers (even those separated by many other layers), by multiplying out their interactions through the residual stream. These virtual weights are the product of the output weights of one layer with the input weights Note that for attention layers, there are three different kinds of input weights: W_Q, W_K, and W_V. For simplicity and generality, we think of layers as just having input and output weights here. of another (ie. W_{I}^2W_{O}^1), and describe the extent to which a later layer reads in the information written by a previous layer.

![Image 3](blob:http://localhost/89da513eccc33f700156bd74ae1538e3)
#### Subspaces and Residual Stream Bandwidth

The residual stream is a high-dimensional vector space. In small models, it may be hundreds of dimensions; in large models it can go into the tens of thousands. This means that layers can send different information to different layers by storing it in different subspaces. This is especially important in the case of attention heads, since every individual head operates on comparatively small subspaces (often 64 or 128 dimensions), and can very easily write to completely disjoint subspaces and not interact.

Once added, information persists in a subspace unless another layer actively deletes it. From this perspective, dimensions of the residual stream become something like "memory" or "bandwidth". The original token embeddings, as well as the unembeddings, mostly interact with a relatively small fraction of the dimensions.We performed PCA analysis of token embeddings and unembeddings. For models with large d_\text{model}, the spectrum quickly decayed, with the embeddings/unembeddings being concentrated in a relatively small fraction of the overall dimensions. To get a sense for whether they occupied the same or different subspaces, we concatenated the normalized embedding and unembedding matrices and applied PCA. This joint PCA process showed a combination of both "mixed" dimensions and dimensions used only by one; the existence of dimensions which are used by only one might be seen as a kind of upper bound on the extent to which they use the same subspace. This leaves most dimensions "free" for other layers to store information in.

It seems like we should expect residual stream bandwidth to be in very high demand! There are generally far more "computational dimensions" (such as neurons and attention head result dimensions) than the residual stream has dimensions to move information. Just a single MLP layer typically has four times more neurons than the residual stream has dimensions. So, for example, at layer 25 of a 50 layer transformer, the residual stream has 100 times more neurons as it has dimensions before it, trying to communicate with 100 times as many neurons as it has dimensions after it, somehow communicating in superposition! We call tensors like this ["bottleneck activations"](https://transformer-circuits.pub/2021/framework/index.html#def-bottleneck-activation) and expect them to be unusually challenging to interpret. (This is a major reason why we will try to pull apart the different streams of communication happening through the residual stream apart in terms of virtual weights, rather than studying it directly.)

Perhaps because of this high demand on residual stream bandwidth, we've seen hints that some MLP neurons and attention heads may perform a kind of "memory management" role, clearing residual stream dimensions set by other layers by reading in information and writing out the negative version.Some MLP neurons have very negative cosine similarity between their input and output weights, which may indicate deleting information from the residual stream. Similarly, some attention heads have large negative eigenvalues in their W_OW_V matrix and primarily attend to the present token, potentially serving as a mechanism to delete information. It's worth noticing that while these may be generic mechanisms for "memory management" deletion of information, they may also be mechanisms for conditionally deleting information, operating only in some cases.

![Image 4](blob:http://localhost/e5935e7a5477858c6ef3b01891f10d22)
### Attention Heads are Independent and Additive

As seen above, we think of transformer attention layers as several completely independent attention heads h\in H which operate completely in parallel and each add their output back into the residual stream. But this isn't how transformer layers are typically presented, and it may not be obvious they're equivalent.

In the original Vaswani et al.paper on transformers , the output of an attention layer is described by stacking the result vectors r^{h_1}, r^{h_2},..., and then multiplying by an output matrix W_O^H. Let's split W_O^H into equal size blocks for each head [W_O^{h_1}, W_O^{h_2}...]. Then we observe that:

W_O^H \left[\begin{matrix}r^{h_1}\\r^{h_2}\\... \end{matrix}\right] ~~=~~ \left[W_O^{h_1},~ W_O^{h_2},~ ... \right]\cdot\left[\begin{matrix}r^{h_1}\\r^{h_2}\\...\end{matrix}\right] ~~=~~ \sum_i W_O^{h_i} r^{h_i}

Revealing it to be equivalent to running heads independently, multiplying each by its own output matrix, and adding them into the residual stream. The concatenate definition is often preferred because it produces a larger and more compute efficient matrix multiply. But for understanding transformers theoretically, we prefer to think of them as independently additive.

### Attention Heads as Information Movement

But if attention heads act independently, what do they do? The fundamental action of attention heads is moving information.They read information from the residual stream of one token, and write it to the residual stream of another token. The main observation to take away from this section is that which tokens to move information from is completely separable from what information is “read” to be moved and how it is “written” to the destination.

![Image 5](blob:http://localhost/cc2ad55cdf9b6a869322adbd53923d7c)
To see this, it’s helpful to write attention in a non-standard way. Given an attention pattern, computing the output of an attention head is typically described in three steps:

1.   Compute the value vector for each token from the residual stream (v_i = W_V x_i).
2.   Compute the “result vector” by linearly combining value vectors according to the attention pattern (r_i = \sum_j A_{i,j} v_j).
3.   Finally, compute the output vector of the head for each token (h(x)_i = W_O r_i).As discussed above, often multiplication by the output matrix is written as one matrix multiply applied to the concatenated results of all heads; however this version is equivalent.

Each of these steps can be written as matrix multiply: why don’t we collapse them into a single step? If you think of x as a 2d matrix (consisting of a vector for each token), we’re multiplying it on different sides. W_V and W_O multiply the “vector per token” side, while A multiplies the “position” side. Tensors can offer us a much more natural language for describing this kind of map between matrices (if tensor product notation isn't familiar, we've included a [short introduction](https://transformer-circuits.pub/2021/framework/index.html#notation-tensor-product) in the notation appendix). One piece of motivation that may be helpful is to note that we want to express linear maps from matrices to matrices: [n_\text{context},~ d_\text{model}] ~\to~ [n_\text{context},~ d_\text{model}]. Mathematicians call such linear maps "(2,2)-tensors" (they map two input dimensions to two output dimensions). And so tensors are the natural language for expressing this transformation.

Using tensor products, we can describe the process of applying attention as:

h(x)~=~(\text{Id} \otimes W_O)~~\cdot~~

Project result vectors out for each token

(h(x)_i = W_O r_i)

~(A \otimes \text{Id})~~\cdot~~~

Mix value vectors _across_ tokens to compute result vectors

(r_i = \sum_j A_{i,j} v_j)

~(\text{Id} \otimes W_V)~~\cdot~~~

Compute value vector for each token

(v_i=W_V x_i)~~

x

Applying the mixed product property and collapsing identities yields:

h(x) ~=~(A ~~\otimes~~ W_O W_V) ~~~\cdot~~~~~~

A
mixes across tokens while

W_OW_V
acts on each vector independently.

x

What about the attention pattern? Typically, one computes the keys k_i = W_K x_i, computes the queries q_i = W_Q x_i and then computes the attention pattern from the dot products of each key and query vector A = \text{softmax}(q^T k). But we can do it all in one step without referring to keys and queries: A = \text{softmax}(x^T W_Q^T W_K x).

It's worth noting that although this formulation is mathematically equivalent, actually implementing attention this way (ie. multiplying by W_O W_V and W_Q^T W_K) would be horribly inefficient!

#### Observations about Attention Heads

A major benefit of rewriting attention heads in this form is that it surfaces a lot of structure which may have previously been harder to observe:

*   Attention heads move information from the residual stream of one token to another.

*   A corollary of this is that the residual stream vector space — which is often interpreted as a “contextual word embedding” — will generally have linear subspaces corresponding to information copied from other tokens and not directly about the present token.

*   An attention head is really applying two linear operations, A and W_OW_V, which operate on different dimensions and act independently.

*   A governs which token's information is moved from and to.
*   W_O W_V governs which information is read from the source token and how it is written to the destination token.What do we mean when we say that W_{OV}=W_O W_V governs which subspace of the residual stream the attention head reads and writes to when it moves information? It can be helpful to consider the singular value decomposition USV = W_{OV}. Since d_{head} < d_{model}, W_{OV} is low-rank and only a subset of the diagonal entries in S are non-zero. The right singular vectors V describe which subspace of the residual stream being attended to is “read in” (somehow stored as a value vector), while the left singular vectors U describe what subspace of the destination residual stream they are written to.

*   A is the only non-linear part of this equation (being computed from a softmax). This means that if we fix the attention pattern, attention heads perform a linear operation. This also means that, without fixing A, attention heads are “half-linear” in some sense, since the per-token linear operation is constant.
*   W_Q and W_K always operate together. They’re never independent. Similarly, W_O and W_V always operate together as well. 

*   Although they’re parameterized as separate matrices, W_O W_V and W_Q^T W_K can always be thought of as individual, low-rank matrices.
*   Keys, queries and value vectors are, in some sense, superficial. They’re intermediary by-products of computing these low-rank matrices. One could easily reparametrize both factors of the low-rank matrices to create different vectors, but still function identically.
*   Because W_O W_V and W_Q W_K always operate together, we like to define variables representing these combined matrices, W_{OV} = W_O W_V and W_{QK} = W_Q^T W_K.

*   Products of attention heads behave much like attention heads themselves. By the distributive property, (A^{h_2}\otimes W_{OV}^{h_2}) \cdot (A^{h_1}\otimes W_{OV}^{h_1})= (A^{h_2}A^{h_1})\otimes(W_{OV}^{h_2}W_{OV}^{h_1}). The result of this product can be seen as functionally equivalent to an attention head, with an attention pattern which is the composition of the two heads A^{h_2}A^{h_1} and an output-value matrix W_{OV}^{h_2}W_{OV}^{h_1}. We call these “virtual attention heads”, discussed in more depth later.

* * *

## Zero-Layer Transformers

Watch videos covering similar content to this section: [0 layer theory](https://www.youtube.com/watch?v=V3NQaDR3xI4&list=PLoyGOS2WIonajhAVqKUgEMNmeq3nEeM51&index=1)

Before moving on to more complex models, it’s useful to briefly consider a “zero-layer” transformer. Such a model takes a token, embeds it, unembeds it to produce logits predicting the next token:

T ~=~ W_U W_E

Because the model cannot move information from other tokens, we are simply predicting the next token from the present token. This means that the optimal behavior of W_U W_E is to approximate the bigram log-likelihood.This parallels an observation by Levy & Goldberg, 2014 that many early word embeddings can be seen as matrix factorizations of a log-likelihood matrix.

This is relevant to transformers more generally. Terms of the form W_U W_E will occur in the expanded form of equations for every transformer, corresponding to the “direct path” where a token embedding flows directly down the residual stream to the unembedding, without going through any layers. The only thing it can affect is the bigram log-likelihoods. Since other aspects of the model will predict parts of the bigram log-likelihood, it won’t exactly represent bigram statistics in larger models, but it does represent a kind of “residual”. In particular, the W_U W_E term seems to often help represent bigram statistics which aren’t described by more general grammatical rules, such as the fact that “Barack” is often followed by “Obama”. An interesting corollary of this is to note that, though W_U is often referred to as the “un-embedding” matrix, we should not expect this to be the inverse of embedding with W_E.

* * *

## One-Layer Attention-Only Transformers

Watch videos covering similar content to this section: [1 layer theory](https://www.youtube.com/watch?v=7crsHGsh3p8&list=PLoyGOS2WIonajhAVqKUgEMNmeq3nEeM51&index=3), [1 layer results](https://www.youtube.com/watch?v=ZBlHFFE-ng8&list=PLoyGOS2WIonajhAVqKUgEMNmeq3nEeM51&index=4).

We claim that one-layer attention-only transformers can be understood as an ensemble of a bigram model and several "skip-trigram" models (affecting the probabilities of sequences "A… BC").Our use of the term "skip-trigram" to describe sequences of the form "A… BC" is inspired by Mikolov et al.'s use of the term "skip-gram" in their classic paper on word embeddings. Intuitively, this is because each attention head can selectively attend from the present token ("B") to a previous token ("A") and copy information to adjust the probability of possible next tokens ("C").

The goal of this section is to rigorously show this correspondence, and demonstrate how to convert the raw weights of a transformer into interpretable tables of skip-trigram probability adjustments.

### The Path Expansion Trick

Recall that a one-layer attention-only transformer consists of a token embedding, followed by an attention layer (which [independently applies](https://transformer-circuits.pub/2021/framework/index.html#architecture-attn-independent) attention heads), and finally an unembedding:

![Image 6](blob:http://localhost/73e5f819f9c757173ffbc747bb2bef2a)
Using [tensor notation](https://transformer-circuits.pub/2021/framework/index.html#notation-tensor-product) and the [alternative representation of attention heads](https://transformer-circuits.pub/2021/framework/index.html#architecture-attn-as-movement) we previously derived, we can represent the transformer as a product of three terms.

![Image 7](blob:http://localhost/546469206834faf51732e27ea8a437e2)
Our key trick is to simply expand the product. This transforms the product (where every term corresponds to a layer), into a sum where every term corresponds to an end-to-end path.

![Image 8](blob:http://localhost/40c8951c079054bbd1b6674dc2983ac2)
We claim each of these end-to-end path terms is tractable to understand, can be reasoned about independently, and additively combine to create model behavior.

The direct path term, \text{Id} \otimes W_U W_E, also occurred when we looked at the zero-layer transformer. Because it doesn’t move information between positions (that's what \text{Id} \otimes … denotes!), the only thing it can contribute to is the bigram statistics, and it will fill in missing gaps that other terms don’t handle there.

The more interesting terms are the attention head terms.

### Splitting Attention Head terms into Query-Key and Output-Value Circuits

For each attention head h we have a term A^h \otimes (W_UW_{OV}^hW_E) where A^h=\text{softmax}\left( t^T \cdot W_E^T W_{QK}^h W_E \cdot t \right). How can we map these terms to model behavior? And while we’re at it, why do we get these particular products of matrices on our equations?

The key thing to notice is that these terms consist of two separable operations, which are at their heart two [n_\text{vocab},~ n_\text{vocab}] matrices:

*   W_E^T W_{QK}^h W_E — We call this matrix the "query-key (QK) circuit."It provides the attention score for every query and key token. That is, each entry describes how much a given query token "wants" to attend to a given key token.
*   W_UW_{OV}^hW_E — We call this matrix the “Output-Value (OV) circuit.” It describes how a given token will affect the output logits if attended to.

To intuitively understand these products, it can be helpful to think of them as paths through the model, starting and ending at tokens. The QK circuit is formed by tracing the computation of a query and key vector up to their attention head, where they dot product to create a bilinear form. The OV circuit is created by tracing the path computing a value vector and continuing it through up to the logits.

![Image 9](blob:http://localhost/25506e6789be43983cfb1a93c107f491)
The attention pattern is a function of both the source and destination token Technically, it is a function of all possible source tokens from the start to the destination token, as the softmax calculates the score for each via the QK circuit, exponentiates and then normalises, but once a destination token has decided how much to attend to a source token, the effect on the output is solely a function of that source token. That is, if multiple destination tokens attend to the same source token the same amount, then the source token will have the same effect on the logits for the predicted output token.

#### OV and QK Independence (The Freezing Attention Patterns Trick)

Thinking of the OV and QK circuits separately can be very useful, since they're both individually functions we can understand (linear or bilinear functions operating on matrices we understand).

But is it really principled to think about them independently? One thought experiment which might be helpful is to imagine running the model twice. The first time you collect the attention patterns of each head. This only depends on the QK circuit.In models with more than one layer, we'll see that the QK circuit can be more complicated than W_E^T W_{QK}^h W_E. The second time, you replace the attention patterns with the "frozen" attention patterns you collected the first time. This gives you a function where the logits are a linear function of the tokens! We find this a very powerful way to think about transformers.

### Interpretation as Skip-Trigrams

One of the core challenges of mechanistic interpretability is to make neural network parameters meaningful by contextualizing them (see discussion by Voss et al.in [Visualizing Weights](https://distill.pub/2020/circuits/visualizing-weights/)). By multiplying out the OV and QK circuits, we've succeeded in doing this: the neural network parameters are now simple linear or bilinear functions on tokens. The QK circuit determines which "source" token the present "destination" token attends back to and copies information from, while the OV circuit describes what the resulting effect on the "out" predictions for the next token is. Together, the three tokens involved form a "skip-trigram" of the form `[source]... [destination][out]`, and the "out" is modified.

It's important to note that this doesn't mean that interpretation is trivial. For one thing, the resulting matrices are enormous (our vocabulary is ~50,000 tokens, so a single expanded OV matrix has ~2.5 billion entries); we revealed the one-layer attention-only model to be a compressed Chinese room, and we're left with a giant pile of cards. There's also all the usual issues that come with understanding the weights of generalized linear models acting on correlated variables and fungibility between variables. For example, an attention head might have a weight of zero because another attention head will attend to the same token and perform the same role it would have. Finally, there's a technical issue where QK weights aren't comparable between different query vectors, and there isn't a clear right answer as to how to normalize them.

Despite this, we do have transformers in a form where all parameters are contextualized and understandable. And despite these subtleties, we can simply read off skip-trigrams from the joint OV and QK matrices. In particular, searching for large entries in these matrices reveals lots of interesting behavior.

In the following subsections, we give a curated tour of some interesting skip-trigrams and how they're embedded in the QK/OV circuits. But full, non-cherrypicked examples of the largest entries in several models are available by following the links:

*   [**Large QK/OV entries — 12 heads, d_head=64**](https://transformer-circuits.pub/2021/framework/head_dump/small_a.html)
*   [**Large QK/OV entries — 32 heads, d_head=128**](https://transformer-circuits.pub/2021/framework/head_dump/larger.html)

#### Copying / Primitive In-Context Learning

One of the most striking things about looking at these matrices is that most attention heads in one layer models dedicate an enormous fraction of their capacity to copying. The OV circuit sets things up so that tokens, if attended to by the head, increase the probability of that token, and to a lesser extent, similar tokens. The QK circuit then only attends back to tokens which could plausibly be the next token. Thus, tokens are copied, but only to places where bigram-ish statistics make them seem plausible.

![Image 10](blob:http://localhost/6ee10f0407f02ecfb281e983125df0c4)
In the above example, we fix a given source token and look at the largest corresponding QK entries (the destination token) and largest corresponding OV entries (the out token). The source token is selected to show interesting behavior, but the destination and out token are the top entries unless entries are explicitly skipped with an ellipsis; they are colored by the intensity of their value in the matrix.

Most of the examples are straightforward, but two deserve explanation: the fourth example (with skip-trigrams like `lambda… $\lambda`) appears to be the model learning LaTeX, while the fifth example (with the skip-trigram `nbsp… >&nbsp`) appears to be the model learning HTML escape sequences.

Note that most of these examples are copying; this appears to be very common.

We also see more subtle kinds of copying. One particularly interesting one is related to how tokenization for transformers typically works. Tokenizers typically merge spaces onto the start of words. But occasionally a word will appear in a context where there isn't a space in front of it, such as at the start of a new paragraph or after a dialogue open quote. These cases are rare, and as such, the tokenization isn't optimized for them. So for less common words, it's quite common for them to map to a single token when a space is in front of them (`" Ralph" → [" Ralph"]`) but split when there isn't a space (`"Ralph" → ["R", "alph"]`).

It's quite common to see skip-trigram entries dealing with copying in this case. In fact, we sometimes observe attention heads which appear to partially specialize in handling copying for words that split into two tokens without a space. When these attention heads observe a fragmented token (e.g. `"R"`) they attend back to tokens which might be the complete word with a space (`" Ralph"`) and then predict the continuation (`"alph"`). (It's interesting to note that this could be thought of as a very special case where a one-layer model can kind of mimic the [induction heads](https://transformer-circuits.pub/2021/framework/index.html#induction-heads) we'll see in two layer models.)

![Image 11](blob:http://localhost/66e3035507db8eddae0b935ab9da5854)
We can summarize this copying behavior into a few abstract patterns that we've observed:

![Image 12](blob:http://localhost/b829a59ae0d2508a1dba99eca1e9a574)
All of these can be seen as a kind of very primitive in-context learning. The ability of transformers to adapt to their context is one of their most interesting properties, and this kind of simple copying is a very basic form of it. However, we'll see when we look at a two-layer transformer that a much more interesting and powerful algorithm for in-context learning is available to deeper transformers.

#### Other Interesting Skip-Trigrams

Of course, copying isn't the only behavior these attention heads encode.

Skip-trigrams seem trivial, but can actually produce more complex behavior than one might expect. Below are some particularly striking skip-trigram examples we found in looking through the largest entries in the expanded OV/QK matrices of our models.

*   [Python] Predicting that the python keywords `else`, `elif` and `except` are more likely after an indentation is reduced using skip-trigrams of the form: `\n\t\t\t … \n\t\t → else/elif/except` where the first part is indented N times, and the second part N-1, for various values of N, and where the whitespace can be tabs or spaces. 
*   [Python]Predicting that `open()` will have a file mode string argument: `open … "," → [rb / wb / r / w]` (for example `open("abc.txt","r")`)
*   [Python]The first argument to a function is often `self`: `def … ( → self` (for example `def method_name(self):`)
*   [Python]In Python 2, `super` is often used to call `.__init__()` after being invoked on `self`: `super … self → ).__` (for example `super(Parent, self).__init__()`)
*   [Python]increasing probability of method/variables/properties associated with a library: `upper … . → upper/lower/capitalize/isdigit`, `tf … . → dtype/shape/initializer`, `datetime… → date / time / strftime / isoformat`, `QtWidgets … . → QtCore / setGeometry / QtGui`, `pygame … . → display / rect / tick`
*   [Python]common patterns `for... in [range/enumerate/sorted/zip/tqdm]`
*   [HTML]`tbody` is often followed by `<td>` tags: `tbody … < → td`
*   [Many]Matching of open and closing brackets/quotes/punctuation: `(** … X → **)`, `(' … X → ')` , `"% … X → %"` , `'</ … X → >'` (see [32 head model, head 0:27](https://transformer-circuits.pub/2021/framework/head_dump/larger.html#head-0-27))
*   [LaTeX] In LaTeX, every `\left` command must have a corresponding `\right` command; conversely `\right` can only happen after a `\left`. As a result, the model predicts that future LaTeX commands are more likely to be `\right` after `\left`: `left … \ → right`
*   [English]Common phrases and constructions (e.g. `keep … [in → mind / at → bay / under → wraps]`, `difficult … not → impossible`)

*   For a single head, here are some trigrams associated with the query `" and"`: `back and → forth`, `eat and → drink`, `trying and → failing`, `day and → night`, `far and → away`, `created and → maintained`, `forward and → backward`, `past and → present`, `happy and → satisfied`, `walking and → talking`, `sick and → tired`, … (see [12 head model, head 0:0](https://transformer-circuits.pub/2021/framework/head_dump/small_a.html#head-0-0))

*   [URLs]Common URL schemes: `twitter … / → status`, `github … / → [issues / blob / pull / master]`, `gmail … . → com`, `http … / → [www / google / localhost / youtube / amazon]`, `http … : → [8080 / 8000]`, `www … . → [org / com / net]`

One thing to note is that the learned skip-trigrams are often related to idiosyncrasies of one's tokenization. For example collapsing whitespace together allows individual tokens to reveal indentation. Not merging backslash into text tokens means that when the model is predicting LaTeX, there's a token after backslash that must be an escape sequence. And so on.

Many skip tri-grams can be difficult to interpret without specific knowledge (e.g. `Israel … K → nes` only makes sense if you know Israel's legislative body is called the "Knesset"). A useful tactic can be to try typing potential skip tri-grams into Google search (or similar tools) and look at autocompletions.

#### Primarily Positional Attention Heads

Our treatment of attention heads hasn't discussed how attention heads handle position, largely because there are now several competing methods(e.g.) and they would complicate our equations. (In the case of standard positional embeddings, the one-layer math works out to multiplying W_{QK} by the positional embeddings.)

In practice, the one-layer models tend to have a small number of attention heads that are primarily positional, strongly preferring certain relative positions. Below, we present one attention head which either attends to the present token or the previous token.How can a one layer model learn an attention head that attends to a relative position? For a position mechanism that explicitly encodes relative position like rotary  the answer is straightforward. However, we use a mechanism similar to  (and, for the purposes of this point, ) where each token index has a position embedding that affects keys and queries. Let's assume that the embeddings are either fixed to be sinusoidal, or the model learns to make them sinusoidal. Observe that, in such an embedding, translation is equivalent to multiplication by a rotation matrix. Then W_{QK} can select for any relative positional offset by appropriately rotating the dimensions containing sinusoidal information.

![Image 13](blob:http://localhost/123cf96250f91dbc82b05bc9a1678992)
#### Skip-Trigram "Bugs"

One of the most interesting things about looking at the expanded QK and OV matrices of one layer transformers is that they can shed light on transformer behavior that seems incomprehensible from the outside.

Our one-layer models represent skip-trigrams in a "factored form" split between the OV and QK matrices. It's kind of like representing a function f(a,b,c) = f_1(a,b) f_2(a,c). They can't really capture the three way interactions flexibly. For example, if a single head increases the probability of both `keep… in mind` and `keep… at bay`, it must also increase the probability of `keep… in bay` and `keep… at mind`. This is likely a good trade for the model on balance, but is also, in some sense, a bug. We frequently observe these in attention heads.

![Image 14](blob:http://localhost/42b4cffed519bad64ce5dba94bee183e)
Highlighted text denotes skip-trigram continuations that the model presumably ideally wouldn't increase the probability of. Note that `QCanvas`[is a class](https://doc.qt.io/archives/3.3/qcanvas.html) involving pixmaps in the popular Qt library. `Lloyd... Catherine` likely refers to Catherine Lloyd Burns. These examples are slightly cherry-picked to be interesting, but very common if you look at the expanded weights for models linked above.

Even though these particular bugs seem in some sense trivial, we’re excited about this result as an early demonstration of using interpretability to understand model failures. We have not further explored this phenomenon, but we’d be curious to do so in more detail. For instance, could we characterize how much performance (in points of loss or otherwise) these “bugs” are costing the model? Does this particular class continue to some extent in larger models (presumably partially, but not completely, masked by other effects)?

### Summarizing OV/QK Matrices

We've turned the problem of understanding one-layer attention-only transformers into the problem of understanding their expanded OV and QK matrices. But as mentioned above, the expanded OV and QK matrices are enormous, with easily billions of entries. While searching for the largest entries is interesting, are there better ways to understand them? There are at least three reasons to expect there are:

*   The OV and QK matrices are extremely low-rank. They are 50,000 × 50,000 matrices, but only rank d_\text{head} (64 or 128). In some sense, they're quite small even though they appear large in their expanded form.
*   Looking at individual entries often reveals hints of much simpler structure. For example, we observe one head where names of people all have the top queries like`" by"` (e.g. `"Anne… by → Anne"`) while location names have top queries like`" from"`(e.g. `"Canada… from → Canada"`). This hints at something like cluster structure in the matrix.
*   Copying behavior is widespread in OV matrices and arguably one of the most interesting behaviors. (We'll see in the next section that there's analogous QK matrix structure in two layer models that's used to search for similar tokens to a query.) It seems like it should be possible to formalize this.

We don't yet feel like we have a clear right answer, but we're optimistic that the right kind of matrix decomposition or dimensionality reduction could be highly informative. (See the technical details appendix for notes on how to efficiently work with these large matrices.)

#### Detecting Copying Behavior

The type of behavior we're most excited to detect in an automated way is copying. Since copying is fundamentally about mapping the same vector to itself (for example, having a token increase its own probability) it seems unusually amenable to being captured in some kind of summary statistic.

However, we've found it hard to pin down exactly what the right notion is; this is likely because there are lots of slightly different ways one could draw the boundaries of whether something is a "copying matrix" and we're not yet sure what the most useful one is. For example, we don't observe this in the models discussed in this paper, but in slightly larger models we often observe attention heads which "copy" some mixture of gender, plurality, and tense from nearby words, helping the model use the correct pronouns and conjugate verbs. The matrices for these attention heads aren't exactly copying individual tokens, but it seems like they are copying in some very meaningful sense. So copying is actually a more complex concept than it might first appear.

One natural approach might be to use eigenvectors and eigenvalues. Recall that v_i is an eigenvector of the matrix M with an eigenvalue \lambda_i if Mv_i = \lambda_i v_i. Let's consider what that means for an OV circuit M=W_UW^h_{OV}W_E if \lambda_i is a positive real number.Then we're saying that there's a linear combination of tokens Before token embedding, we think of tokens as being one-hot vectors in a very high-dimensional space. Logits are also vectors. As a result, we can think about linear combinations of tokens in both spaces. which increases the linear combination of logits of those same tokens.Very roughly you could think of this as a set of tokens (perhaps all tokens representing plural words for a very broad one, or all tokens starting with a given first letter, or all tokens representing different capitalizations and inclusions of space for a single word for a narrow one) which mutually increase their own probability. Of course, in general we expect the eigenvectors have both positive and negative entries, so it's more like there are two sets of tokens (e.g. tokens representing male and female words, or tokens representing singular and plural words) which increase the probability of other tokens in the same set and decrease those in others.

The eigendecomposition expresses the matrix as a set of such eigenvectors and eigenvalues. For a random matrix, we expect to have an equal number of positive and negative eigenvalues, and for many to be complex.The most similar class of random matrix for which eigenvalues are well characterized is likely Ginibre matrices, which have Gaussian-distributed entries similar to our neural network matrices at initialization. Real valued Ginibre matrices are known to have positive-negative symmetric eigenvalues, with extra probability mass on the real numbers, and "repulsion" near them . Of course, in practice we are dealing with products of matrices, but empirically the distribution of eigenvalues for the OV circuit with our randomly initialized weights appears to mirror the Ginibre distribution.  But copying requires positive eigenvalues, and indeed we observe that many attention heads have positive eigenvalues, apparently mirroring the copying structure:

![Image 15](blob:http://localhost/e08306e06d2394aae35e5f8ad68c2150)
One can even collapse that down further and get a histogram of how many of the attention heads are copying (if one trusts the eigenvalues as a summary statistic):

![Image 16](blob:http://localhost/bf11d96b7cabba35df1e91ada3cc48e6)
It appears that 10 out of 12 heads are significantly copying! (This agrees with qualitative inspection of the expanded weights.)

But while copying matrices must have positive eigenvalues, it isn't clear that all matrices with positive eigenvalues are things we necessarily want to consider to be copying. A matrix's eigenvectors aren't necessarily orthogonal, and this allows for pathological examples;Non-orthogonal eigenvectors can have unintuitive properties. If one tries to express a matrix in terms of eigenvectors, one needs to multiply by the inverse of the eigenvector matrix, which can behave quite differently than naively projecting onto the eigenvectors in the non-orthogonal case.for example, there can be matrices with all positive eigenvalues that actually map some tokens to decreasing the logits of that same token.Positive eigenvalues still mean that the matrix is, in some sense, "copying on average", and they're still quite strong evidence of copying in that they seem improbable by default and empirically seem to align with copying. But they shouldn't be considered a dispositive proof that a matrix is copying in all senses one might reasonably mean.

One might try to formalize "copying matrices" in other ways. One possibility is to look at the diagonal of a matrix, which describes how each token affects its own probability. As expected, entries on the diagonal are very positive-leaning. We can also ask how often a random token increases its own probability more than any other token (or is one of the k-most increased tokens, to allow for tokens which are the same with a different capitalization or with a space).All of these seem to point in the direction of these attention heads being copying matrices, but it's not clear that any of them is a fully robust formalization of "the primary behavior of this matrix is copying". It's worth noting that all of these potential notions of copying are linked by the fact that the sum of the eigenvalues is equal to the trace is equal to the sum of the diagonal.

For the purposes of this paper, we'll continue to use the eigenvalue-based summary statistic. We don't think it's perfect, but it seems like quite strong evidence of copying, and empirically aligns with manual inspection and other definitions.

### Do We "Fully Understand" One-Layer Models?

There's often skepticism that it's even possible or worth trying to truly reverse engineer neural networks. That being the case, it's tempting to point at one-layer attention-only transformers and say "look, if we take the most simplified, toy version of a transformer, at least that minimal version can be fully understood."

But that claim really depends on what one means by fully understood. It seems to us that we now understand this simplified model in the same sense that one might look at the weights of a giant linear regression and understand it, or look at a large database and understand what it means to query it. That is a kind of understanding. There's no longer any algorithmic mystery. The contextualization problem of neural network parameters has been stripped away. But without further work on summarizing it, there's far too much there for one to hold the model in their head.

Given that regular one layer neural networks are just generalized linear models and can be interpreted as such, perhaps it isn't surprising that a single attention layer is mostly one as well.

* * *

## Two-Layer Attention-Only Transformers

Videos covering similar content to this section: [2 layer theory](https://www.youtube.com/watch?v=UM-eJbx_YDk&list=PLoyGOS2WIonajhAVqKUgEMNmeq3nEeM51&index=5), [2 layer term importance](https://www.youtube.com/watch?v=qom0nxou4f4&list=PLoyGOS2WIonajhAVqKUgEMNmeq3nEeM51&index=6), [2 layer results](https://www.youtube.com/watch?v=VuxANJDXnIY&list=PLoyGOS2WIonajhAVqKUgEMNmeq3nEeM51&index=7)

Deep learning studies models that are deep, which is to say they have many layers. Empirically, such models are very powerful. Where does that power come from? One intuition might be that depth allows composition, which creates powerful expressiveness.

Composition of attention heads is the key difference between one-layer and two-layer attention-only transformers. Without composition, a two-layer model would simply have more attention heads to implement skip-trigrams with. But we'll see that in practice, two-layer models discover ways to exploit attention head composition to express a much more powerful mechanism for accomplishing in-context learning. In doing so, they become something much more like a computer program running an algorithm, rather than look-up tables of skip-trigrams we saw in one-layer models.

### Three Kinds of Composition

Recall that we think of the residual stream [as a communication channel](https://transformer-circuits.pub/2021/framework/index.html#residual-comms). Every attention head reads in subspaces of the residual stream determined by W_Q, W_K, and W_V, and then writes to some subspace determined by W_O. Since the attention head vectors are much smaller than the size of the residual stream (typical values of d_\text{head} / d_\text{model} might vary from around 1/10 to 1/100), attention heads operate on small subspaces and can easily avoid significant interaction.

When attention heads do compose, there are three options:

*   Q-Composition: W_Q reads in a subspace affected by a previous head.
*   K-Composition: W_K reads in a subspace affected by a previous head.
*   V-Composition: W_V reads in a subspace affected by a previous head.

Q- and K-Composition are quite different from V-Composition. Q- and K-Composition both affect the attention pattern, allowing attention heads to express much more complex patterns. V-Composition, on the other hand, affects what information an attention head moves when it attends to a given position; the result is that V-composed heads really act more like a single unit and can be thought of as creating an additional "virtual attention heads".Composing movement of information with movement of information gives movement of information, whereas attention heads affecting attention patterns is not reducible in this way.

To really understand these three kinds of composition, we'll need to study the OV and QK circuits again.

### Path Expansion of Logits

The most basic question we can ask of a transformer is "how are the logits computed?" Following [our approach](https://transformer-circuits.pub/2021/framework/index.html#onel-path-expansion) to the one-layer model, we write out a product where every term is a layer in the model, and expand to create a sum where every term is an end-to-end path through the model.

![Image 17](blob:http://localhost/0abad8fa592202dc3cd139e3c4bd2228)
Two of these terms, the direct path term and individual head terms, are identical to the one-layer model. The final "virtual attention head" term corresponds to V-Composition.Virtual attention heads are conceptually very interesting, and we'll discuss them more later. However, in practice, we'll find that they tend to not play a significant role in small two-layer models.

### Path Expansion of Attention Scores QK Circuit

Just looking at the logit expansion misses what is probably the most radically different property of a two-layer attention-only transformer: Q-composition and K-composition cause them to have much more expressive second layer attention patterns.

To see this, we need to look at the QK circuits computing the attention patterns. Recall that the attention pattern for a head h is A^h~=~ \text{softmax}^*\!\left( t^T \cdot C_{QK}^h t \right), where C_{QK}^h is the "QK-circuit" mapping tokens to attention scores. For first layer attention heads, the QK-circuit is just the same matrix we saw in the one-layer model: C^{\,h\in H_1}_{\,QK}~=~ W_E^T W_{QK}^h W_E.

But for the second layer QK-circuit, both Q-composition and K-composition come into play, with previous layer attention heads potentially influencing the construction of the keys and queries. Ultimately, W_{QK} acts on the residual stream. In the case of the first layer this reduced to just acting on the token embeddings: C^{\,h\in H_1}_{\,QK}~=~ x_0^T W_{QK}^h x_0=~ W_E^T W_{QK}^h W_E. But by the second layer, C^{\,h\in H_2}_{\,QK}~=~ x_1^T W_{QK}^h x_1 is acting on x_1, the residual stream after first layer attention heads. We can write this down as a product, with the first layer both on the "key side" and "query side."Then we apply our path expansion trick to the product.

One complicating factor is that we have to write it as a 6-dimensional tensor, using two tensor products on matrices. This is because we're trying to express a multilinear function of the form [n_\text{context},~ d_\text{model}] \times [n_\text{context},~ d_\text{model}] ~\to~ [n_\text{context},~ n_\text{context}]. In the one-layer case, we could side step this by implicitly doing an outer product, but that no longer works. A natural way to express this is as a (4,2)-tensor (one with 4 input dimensions and 2 output dimensions). Each term will be of the form A_q \otimes A_k \otimes W where x (A_q \otimes A_k \otimes W) y = A_q^T x W y A_k, meaning that A_q describes the movement of query-side information between tokens, A_k describes the movement of key-side information between tokens, and W describes how they product together to form an attention score.

![Image 18](blob:http://localhost/eb4dfd8fb98e8119e6ae7a95618d935e)
Each of these terms corresponds to a way the model can implement more complex attention patterns. In the abstract, it can be hard to reason about them. But we'll return to them with a concrete case shortly, when we talk about induction heads.

### Analyzing a Two-Layer Model

So far, we've developed a theoretical model for understanding two-layer attention-only models. We have an overall equation describing the logits (the OV circuit), and then an equation describing how each attention head's attention pattern is computed (the QK circuit). But how do we understand them in practice? In this section, we'll reverse engineer a single two-layer model.

Recall that the key difference between a two-layer model and a one-layer model is Q-, K-, and V-composition. Without composition, the model is just a one-layer model with extra heads.

Small two-layer models seem to often (though not always) have a very simple structure of composition, where the only type of composition is K-composition between a single first layer head and some of the second layer heads.There appears to be no significant V- or Q- composition in this particular model. The following diagram shows Q-, K-, and V-composition between first and second layer heads in the model we wish to analyze. We've colored the heads involved by our understanding of their behavior. The first layer head has a very simple attention pattern: it primarily attends to the previous token, and to a lesser extent the present token and the token two back. The second layer heads are what we call _induction heads_.

![Image 19](blob:http://localhost/b61449ecde3da48838fd9dbd422c2c5b)
The above diagram shows Q-, K-, and V-Composition between attention heads in the first and second layer. That is, how much does the query, key or value vector of a second layer head read in information from a given first layer head? This is measured by looking at the Frobenius norm of the product of the relevant matrices, divided by the norms of the individual matrices. For Q-Composition, ||W_{QK}^{h_2~T}W_{OV}^{h_1}||_F / (||W_{QK}^{h_2~T}||_F ||W_{OV}^{h_1}||_F), for K-Composition ||W_{QK}^{h_2}W_{OV}^{h_1}||_F / (||W_{QK}^{h_2}||_F ||W_{OV}^{h_1}||_F), for V-Composition ||W_{OV}^{h_2}W_{OV}^{h_1}||_F / (||W_{OV}^{h_2}||_F ||W_{OV}^{h_1}||_F). By default, we subtract off the empirical expected amount for random matrices of the same shapes (most attention heads have a much smaller composition than random matrices). In practice, for this model, there is only significant K-composition, and only with one layer 0 head.

One quick observation from this is that most attention heads are not involved in any substantive composition.We can think of them as, roughly, a larger collection of skip tri-grams. This two-layer model has a mystery for us to figure out, but it's a fairly narrowly scoped one.(We speculate this means that having a couple induction heads in some sense "outcompetes" a few potential skip-trigram heads, but no other type of composition did. That is, having more skip-trigram heads is a competitive use of second layer attention heads in a small model.)

In the next few sections, we'll develop a theory of what's going on, but before we do, we provide an opportunity to poke around at the attention heads using the interactive diagram below, which displays value-weighted attention patterns over the first paragraph of _Harry Potter and the Philosopher's Stone_. We've colored the attention heads involved in K-composition using the same scheme as above. (This makes it a bit hard to investigate the other heads; if you want to look at those, an interface for general exploration is available [here](https://transformer-circuits.pub/2021/framework/2L_HP_normal.html)).

We recommend isolating individual heads and both looking at the pattern and hovering over tokens. For induction heads, note especially the off-diagonal lines in the attention pattern, and the behavior on the tokens compositing Dursley and Potters.

Attention Pattern

Attention Heads (hover to focus, click to lock)

0:0

0:1

0:2

0:3

0:4

0:5

0:6

0:7

0:8

0:9

0:10

0:11

1:0

1:1

1:2

1:3

1:4

1:5

1:6

1:7

1:8

1:9

1:10

1:11

Tokens (hover to focus, click to lock)

<START>

Mr

and

Mrs

D

urs

ley

,

of

number

four

,

Pri

vet

Drive

,

were

proud

to

say

that

they

were

perfectly

normal

,

thank

you

very

much

.

They

were

the

last

people

you

'd

expect

to

be

involved

in

anything

strange

or

mysterious

,

because

they

just

didn

't

hold

with

such

nonsense

.

Mr

D

urs

ley

was

the

director

of

a

firm

called

G

run

nings

,

which

made

dr

ills

.

He

was

a

big

,

beef

y

man

with

hardly

any

neck

,

although

he

did

have

a

very

large

m

oust

ache

.

Mrs

D

urs

ley

was

thin

and

blonde

and

had

nearly

twice

the

usual

amount

of

neck

,

which

came

in

very

useful

as

she

spent

so

much

of

her

time

cran

ing

over

garden

fences

,

spy

ing

on

the

neighbours

.

The

D

urs

leys

had

a

small

son

called

Dudley

and

in

their

opinion

there

was

no

finer

boy

anywhere

.

The

D

urs

leys

had

everything

they

wanted

,

but

they

also

had

a

secret

,

and

their

greatest

fear

was

that

somebody

would

discover

it

.

They

didn

't

think

they

could

bear

it

if

anyone

found

out

about

the

Pot

ters

.

Mrs

Potter

was

Mrs

D

urs

ley

's

sister

,

but

they

hadn

't

met

for

several

years

;

in

fact

,

Mrs

D

urs

ley

preten

ded

she

didn

't

have

a

sister

,

because

her

sister

and

her

good

-

for

-

nothing

husband

were

as

un

D

urs

ley

ish

as

it

was

possible

to

be

.

The

D

urs

leys

shuddered

to

think

what

the

neighbours

would

say

if

the

Pot

ters

arrived

in

the

street

.

The

D

urs

leys

knew

that

the

Pot

ters

had

a

small

son

,

too

,

but

they

had

never

even

seen

him

.

This

boy

was

another

good

reason

for

keeping

the

Pot

ters

away

;

they

didn

't

want

Dudley

mixing

with

a

child

like

that

.

The above diagram shows the _value-weighted attention pattern_ for various attention heads; that is, the attention patterns with attention weights scaled by the norm of the value vector at the source position

||v_{src}^h||
. You can think of the value-weighted attention pattern as showing "how big a vector is moved from each position." (This approach was also recently introduced by Kobayashi et al.

.) This is especially useful because attention heads will sometimes use certain tokens as a kind of default or resting position when there isn't a token that matches what they're looking for; the value vector at these default positions will be small, and so the value weighted pattern is more informative.

The interface allows one to isolate attention heads, shows the overall attention pattern, and allows one to explore the attention for individual tokens. Attention heads involved in K-composition are colored using the same scheme as above. We suggest trying to isolate these heads.

If you look carefully, you'll notice that the aqua colored "induction heads" often attend back to previous instances of the token which _will_ come next. We'll investigate this more in the next section. Of course, looking at attention patterns on a single piece of text — especially a well-known paragraph like this one — can't give us very high confidence as to how these heads behave in generality. We'll return to this later, once we have a stronger hypothesis of what's going on.

### Induction Heads

In small two-layer attention-only transformers, composition seems to be primarily used for one purpose: the creation of what we call induction heads. We previously saw that the one-layer model dedicated a lot of its capacity to copying heads, as a crude way to implement in-context learning. Induction heads are a much more powerful mechanism for achieving in-context learning. (We will explore the role of induction heads in in-context learning in more detail in our [next paper](https://transformer-circuits.pub/2022/in-context-learning-and-induction-heads/index.html).)

#### Function of Induction Heads

If you played around with the attention patterns above, you may have already guessed what induction heads do. Induction heads search over the context for previous examples of the present token.If they don't find it, they attend to the first token (in our case, a special token placed at the start), and do nothing. But if they do find it, they then look at the next token and copy it. This allows them to repeat previous sequences of tokens, both exactly and approximately.

It's useful to compare induction heads to the types of in-context learning we observed in one layer models:

*   One layer model copying head: `[b] … [a] → [b]`

*   And when rare quirks of tokenization allow: `[ab] … [a] → [b]`

*   Two layer model induction head: `[a][b] … [a] → [b]`

The two-layer algorithm is more powerful. Rather than generically looking for places it might be able to repeat a token, it knows how the token was previously used and looks out for similar cases. This allows it to make much more confident predictions in those cases. It's also less vulnerable to distributional shift, since it doesn't depend on learned statistics about whether one token can plausibly follow another. (We'll see later that induction heads can operate on repeated sequences of completely random tokens)

The following examples highlight a few cases where induction heads help predict tokens in the first paragraph of Harry Potter:

![Image 20](blob:http://localhost/28de585f795d91b87182a3ccfb293644)
Raw attention pattern and logit effect for the induction head `1:8` on some segments of the first paragraph of _Harry Potter and the Philosopher's Stone_. The "logit effect" value shown is the effect of the result vector for the present token on the logit for the next token, (W_U W_O^h r^h_\text{pres\_tok})_\text{next\_tok}, which is equivalent to running the full OV circuit and inspecting the logit this head contributes to the next token.

Earlier, we promised to show induction heads on more tokens in order to better test our theory of them. We can now do this.

Given that we believe induction heads are attending to previous copies of the token and shifting forward, they should be able to do this on totally random repeated patterns. This is likely the hardest test one can give them, since they can't rely on normal statistics about which tokens typically come after other tokens. Since the tokens are uniformly sampled random tokens from our vocabulary, we represent the n th token in our vocabulary as `<n>`, with the exception of the special token `<START>`. (Notice that this is totally off distribution. Induction heads can operate on wildly different distributions as long as the more abstract property that repeated sequences are more likely to reoccur holds true.)

Attention Pattern

Attention Heads (hover to focus, click to lock)

0:0

0:1

0:2

0:3

0:4

0:5

0:6

0:7

0:8

0:9

0:10

0:11

1:0

1:1

1:2

1:3

1:4

1:5

1:6

1:7

1:8

1:9

1:10

1:11

Tokens (hover to focus, click to lock)

<START>

<21549>

<15231>

<1396>

<5012>

<5767>

<2493>

<7192>

<17468>

<6215>

<14329>

<4652>

<8828>

<36539>

<10496>

<38416>

<5550>

<7671>

<15553>

<35140>

<39966>

<21549>

<15231>

<1396>

<5012>

<5767>

<2493>

<7192>

<17468>

<6215>

<14329>

<4652>

<8828>

<36539>

<10496>

<38416>

<5550>

<7671>

<15553>

<35140>

<39966>

<21549>

<15231>

<1396>

<5012>

<5767>

<2493>

<7192>

<17468>

<6215>

<14329>

<4652>

<8828>

<36539>

<10496>

<38416>

<5550>

<7671>

<15553>

<35140>

<39966>

As in our previous attention pattern diagram, this diagram shows the value-weighted attention pattern for various heads, with each head involved in K-composition colored by our theory. Attention heads are shown acting on a random sequence of tokens, repeated three times.`<n>` denotes the n th token in our vocabulary.

This seems like pretty strong evidence that our hypothesis of induction heads is right. We now know what K-composition is used for in our two layer model. The question now is _how_ K-composition accomplishes it.

#### How Induction Heads Work

The central trick to induction heads is that the key is computed from tokens shifted one token back.For models with position embeddings which are available in the residual stream (unlike rotary attention), a second algorithm for implementing induction heads is available; see our intuitions around position embeddings and pointer arithmetic algorithms in transformers. The query searches for "similar" key vectors, but because keys are shifted, finds the next token.

The following example, from a larger model with more sophisticated induction heads, is a useful illustration:

![Image 21](blob:http://localhost/c3ae2a3f9fb24d9790af9eeda9e1fb2f)
QK circuits can be expanded in terms of tokens instead of attention heads. Above, key and query intensity represent the amount each token increases the attention score. Logit effect is the OV circuit.

The minimal way to create an induction head is to use K-composition with a previous token head to shift the key vector forward one token. This creates a term of the form \text{Id} \otimes A^{h_{-1}} \otimes W in the QK-circuit (where A^{h_{-1}} denotes an attention pattern attending to the previous token). If W matches cases where the tokens are the same — the QK version of a ["copying matrix"](https://transformer-circuits.pub/2021/framework/index.html#copying-matrix) — then this term will increase attention scores when the previous token before the source position is the same as the destination token. (Induction heads can be more complicated than this; for example, other 2-layer models will develop an attention head that attends a bit further than the previous token, presumably to create a A^{h_{-1}} \otimes A^{h_{-2}} \otimes W term so some heads can match back further).

#### Checking the Mechanistic Theory

Our mechanistic theory suggests that induction heads must do two things:

*   Have a "copying" OV circuit matrix.
*   Have a "same matching" QK circuit matrix associated with the \text{Id} \otimes A^{h_{-1}} \otimes W term.

Although we're not confident that the eigenvalue summary statistic from the [Detecting Copying section](https://transformer-circuits.pub/2021/framework/index.html#copying-matrix) is the best possible summary statistic for detecting "copying" or "matching" matrices, we've chosen to use it as a working formalization. If we think of our attention heads as points in a 2D space of QK and OV eigenvalue positivity, all the induction heads turn out to be in an extreme right hand corner.

![Image 22](blob:http://localhost/483218c6dee407ab49c09dc553cc9519)
One might wonder if this observation is circular. We originally looked at these attention heads because they had larger than random chance K-composition, and now we've come back to look, in part, at the K-composition term. But in this case, we're finding that the K-composition creates a matrix that is extremely biased towards positive eigenvalues — there wasn't any reason to suggest that a large K-composition would imply a positive K-composition. Nor any reason for all the OV circuits to be positive.

But that is exactly what we expect if the algorithm implemented is the described algorithm for implementing induction.

### Term Importance Analysis

Earlier, we decided to ignore all the "virtual attention head" terms because we didn't observe any significant V-composition. While that seems like it's probably right, there's ways we could be mistaken. In particular, it could be the case that while every individual virtual attention head wasn't important, they matter in aggregate. This section will describe an approach to double checking this using ablations.

Ordinarily, when we ablate something in a neural network, we're ablating something that's explicitly represented in the activations. We can simply multiply it by zero and we're done. But in this case, we're trying to ablate an implicit term that only exists if you expand out the equations. We could do this by trying to run the version of a transformer described in our equations, but that would be horribly slow, and get exponentially worse as we considered deeper models.

But it turns out there's an algorithm which can determine the marginal effect of ablating the

<!-- media:youtube id="V3NQaDR3xI4" url="https://www.youtube.com/watch?v=V3NQaDR3xI4" -->
<!-- media:youtube id="7crsHGsh3p8" url="https://www.youtube.com/watch?v=7crsHGsh3p8" -->
<!-- media:youtube id="ZBlHFFE-ng8" url="https://www.youtube.com/watch?v=ZBlHFFE-ng8" -->
<!-- media:youtube id="UM-eJbx_YDk" url="https://www.youtube.com/watch?v=UM-eJbx_YDk" -->
<!-- media:youtube id="qom0nxou4f4" url="https://www.youtube.com/watch?v=qom0nxou4f4" -->
<!-- media:youtube id="VuxANJDXnIY" url="https://www.youtube.com/watch?v=VuxANJDXnIY" -->

<!-- media:youtube id="8wYNsoycM1U" url="https://www.youtube.com/watch?v=8wYNsoycM1U" -->

<!-- media:youtube id="4O-JhroSAwA" url="https://www.youtube.com/watch?v=4O-JhroSAwA" -->

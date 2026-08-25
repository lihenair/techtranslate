---
source_url: https://go.dev/blog/go1.27
fetched_at: 2026-08-25T10:57:54Z
fetch_method: jina
issue: 88
title_zh: Go 1.27 发布说明
tech_domain: other
---

# Go 1.27 is released - The Go Programming Language

## [The Go Blog](https://go.dev/blog/)

Today the Go team is pleased to release Go 1.27. You can find its binary archives and installers on the [download page](https://go.dev/dl/).

Go 1.27 brings major enhancements across the language, toolchain, runtime, and standard library. Below are some of the key highlights.

## Language changes

Go 1.27 introduces three notable updates to the [language specification](https://go.dev/doc/go1.27#language).

First, generic methods are now supported. For example, see [`math/rand/v2.Rand`](https://go.dev/pkg/math/rand/v2#Rand):

```
// Prior to Go 1.27, a separate method on Rand had to be added for each type
// (unsigned integer methods omitted for brevity).
func (r *Rand) Int32N(n int32) int32
func (r *Rand) Int64N(n int64) int64
func (r *Rand) IntN(n int) int

// Go 1.27 adds a new generic method that works for all integer types.
func (r *Rand) N[Int intType](n Int) Int
```

Second, a key in a [struct literal](https://go.dev/ref/spec#Composite_literals) may now be any valid [field selector](https://go.dev/ref/spec#Selectors) for the struct type, allowing fields in nested or embedded structs to be initialized directly:

```
type Habitat struct {
    Burrow string
}

type Gopher struct {
    Name    string
    Habitat // Embedded struct.
}

// Go 1.27 allows using Burrow as a key directly.
g := Gopher{
    Name:   "Gopher",
    Burrow: "Burrow #42",
}
```

Finally, function type inference has been generalized to apply in all assignment contexts. Generic functions can now be used without explicit type arguments in composite literals, type conversions, and channel sends:

```
func GenericFormatter[T any](v T) string {
    return fmt.Sprintf("value: %v", v)
}

type IntFormatter func(int) string

// Go 1.27 infers T = int in composite literals, conversions, and channel sends.
formatters := []IntFormatter{GenericFormatter}
fn := IntFormatter(GenericFormatter)
ch := make(chan IntFormatter, 1)
ch <- GenericFormatter
```

## Tool improvements

*   [`go fix`](https://go.dev/doc/go1.27#go-fix) includes several new [modernizers](https://go.dev/pkg/golang.org/x/tools/go/analysis/passes/modernize): `atomictypes`, `embedlit`, `slicesbackward`, and `unsafefuncs`.
*   [`go doc`](https://go.dev/doc/go1.27#go-doc) now supports `package@version` queries such as `go doc example.com/pkg@v1.2.3`.
*   [`go mod tidy`](https://go.dev/doc/go1.27#go-mod-tidy) now automatically consolidates multiple `require` blocks in `go.mod` into a standard direct and indirect two-block structure.

## Performance and runtime

*   [Size-specialized memory allocation](https://go.dev/doc/go1.27#faster-memory-allocation) reduces small object (<80B) allocation costs by up to 30%, improving overall performance by ~1% for allocation-heavy programs.
*   The [`goroutineleak`](https://go.dev/doc/go1.27#goroutineleak-profiles) profile in [`runtime/pprof`](https://go.dev/pkg/runtime/pprof) is now generally available, allowing automatic detection of permanently blocked goroutines.

## Standard library additions

*   [`encoding/json/v2`](https://go.dev/doc/go1.27#jsonv2) provides high-level JSON processing with configurable options and stricter defaults, alongside [`encoding/json/jsontext`](https://go.dev/doc/go1.27#jsonv2) for low-level streaming. The existing [`encoding/json`](https://go.dev/pkg/encoding/json) package is now backed by the v2 implementation for faster unmarshaling while maintaining backwards compatibility.
*   [`crypto/mldsa`](https://go.dev/doc/go1.27#crypto_mldsa) implements the post-quantum ML-DSA signature scheme (FIPS 204), integrated into [`crypto/x509`](https://go.dev/pkg/crypto/x509) and [`crypto/tls`](https://go.dev/pkg/crypto/tls).
*   [`uuid`](https://go.dev/doc/go1.27#uuid) provides native support for generating and parsing UUIDs.
*   [`simd`](https://go.dev/doc/go1.27#simd) and architecture-specific [`simd/archsimd`](https://go.dev/doc/go1.27#archsimd) provide experimental SIMD support.
*   [`net/http/httptest`](https://go.dev/doc/go1.27#nethttphttptestpkgnethttphttptest) adds [`NewTestServer`](https://go.dev/pkg/net/http/httptest#NewTestServer), providing an in-memory fake network suitable for use with the [`testing/synctest`](https://go.dev/pkg/testing/synctest) package.

Please read the [Go 1.27 release notes](https://go.dev/doc/go1.27) for the complete list of changes and details.

Over the next few weeks, follow-up blog posts will cover some of the topics relevant to Go 1.27 in more detail. Check back later to read those posts.

Thanks to everyone who contributed to this release by writing code, filing bugs, trying out experimental additions, and testing release candidates. As always, if you notice any problems, please [file an issue](https://go.dev/issue/new).

We hope you enjoy using Go 1.27!

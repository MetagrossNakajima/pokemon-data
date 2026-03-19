---
name: prefer_type_over_interface
description: TypeScriptではinterfaceよりtype aliasを好む
type: feedback
---

TypeScriptの型定義では `interface` より `type` を使う。

**Why:** ユーザーの好み。
**How to apply:** オブジェクト型を定義するとき `type Foo = { ... }` を使い、`interface Foo { ... }` は使わない。

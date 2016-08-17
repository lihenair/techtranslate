No More findViewById

原文链接：[https://medium.com/google-developers/no-more-findviewbyid-457457644885#.kghy74of1](https://medium.com/google-developers/no-more-findviewbyid-457457644885#.kghy74of1)

一个鲜为人知的使用Android Studio开发Android应用的特点是数据绑定。随之而来的是我会在后面的文章中涉及许多优秀的特性，但最基础的事情是消除findViewById。

这是不是只是颈部疼痛？

```
TextView hello = (TextView) findViewById(R.id.hello);
```

有许多以消除这点代码为主要目标工具可用，但现在Android 1.5和之后有一个官方的方式了。

首先，必须编辑应用的build.gradle文件，在android块中添加如下配置：

```
android {
    …
    dataBinding.enabled = true
}
```

接着修改布局文件，在外出添加\<layout\>来代替使用的ViewGroup：

```
<layout xmlns:android="http://schemas.android.com/apk/res/android"
        xmlns:tools="http://schemas.android.com/tools">
    <RelativeLayout
            android:layout_width="match_parent"
            android:layout_height="match_parent"
            android:paddingLeft="@dimen/activity_horizontal_margin"
            android:paddingRight="@dimen/activity_horizontal_margin"
            android:paddingTop="@dimen/activity_vertical_margin"
            android:paddingBottom="@dimen/activity_vertical_margin"
            tools:context=".MainActivity">

        <TextView
                android:id="@+id/hello"
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"/>

    </RelativeLayout>
</layout>
```

**layout**标签告知Android Studio这个布局在编译时需要附加的处理来找到所有感兴趣的视图并为下一步标记它们。所有不带外部**layout**标签的布局将没有额外处理的步骤，这样你就可以在新工程里使用它，而不需要修改剩余的应用。

下面你需要做的是告知Android Studio在运行时加载不同的布局文件。因为这个工作要追溯到Eclaire发布，不依赖于新架构的变化来加载这些预处理布局文件。因此，必须对加载过程做细微调整。

从一个Activity，不要这样：

```
setContentView(R.layout.hello_world);
TextView hello = (TextView) findViewById(R.id.hello);
hello.setText("Hello World"); // for example, but you'd use
                              // resources, right?
```

而是这样：

```
HelloWorldBinding binding = 
    DataBindingUtil.setContentView(this, R.layout.hello_world);
binding.hello.setText("Hello World"); // you should use resources!
```

这里你看到一个类，**HelloWorldBinding**，为**hello_world.xml**布局文件生成的，ID是"@+id/hello"的视图被分配了可用的一个final域**hello**。没有转型，没有findViewById。

事实证明，这种访问视图的机制不仅比findViewById简单，而且更快！绑定过程一次性遍历布局文件中所有视图，并指定视图的域。当执行findViewById时，视图曾佳每次都要查找id一次。

你会看到他使用驼峰命名变量名(就像hello_world.xml变成HelloWordingBinding)，因此如果ID是"@+id/hello_text"，那么域名将是**helloText**。

当你期望对RecyclerView，ViewPager或其他未设置Activity的内容引入到布局时，你想使用生成的类文件中的类型安全方法。这有一些匹配LayoutInflater的版本，因此使用最适合的一个。例如：

```
HelloWorldBinding binding = HelloWorldBinding.inflate(
    getLayoutInflater(), container, attachToContainer);
```

如果没有连接到引入的视图到包含ViewGroup，你不得不访问要引入的视图的层级。你可以使用绑定的getRoot()方法实现：

```
linearLayout.addView(binding.getRoot());
```

现在，你可能会想，如果我有一些不同视图不同配置的布局怎么办？布局预处理和运行引入阶段通过添加所有视图ID到生成类，并且只把不在引入布局的ID设置为null，来处理这些。

漂亮的魔术，是吧？最美妙的部分是在运行时没有反射或其他高成本的技术。这很容易运用到你当前的应用来让你的生活容易一点点，你的布局加载更快一点。
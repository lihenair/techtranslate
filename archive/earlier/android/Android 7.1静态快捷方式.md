Android 7.1 Static Shortcut

原文链接[https://medium.com/@tonyowen/android-7-1-static-shortcut-6c42d81ba11b#.v59ccd4dj](https://medium.com/@tonyowen/android-7-1-static-shortcut-6c42d81ba11b#.v59ccd4dj)

我已收到崭新的Pixel，这里是一个如何添加应用程序静态快捷方式的快速示例。

![](https://cdn-images-1.medium.com/max/1600/1*exFaVibhueg3LjKAkAtduA.gif)

静态快捷方式定义在xml中。所以在/res/xml/shortcuts.xml中打开你的xml。

```
<shortcuts xmlns:android="http://schemas.android.com/apk/res/android">
    <shortcut
        android:shortcutId="quickStart"
        android:enabled="true"
        android:icon="@drawable/ic_vector_shortcut"
        android:shortcutShortLabel="@string/quickstart"
        android:shortcutLongLabel="@string/quickstart_long"
        android:shortcutDisabledMessage="@string/quickstart_disabled">
        <intent
            android:action="com.your.app.QUICKSTART"
            android:targetPackage="com.your.app"
            android:targetClass="com.your.app.activities.MainActivity" />
    </shortcut>
    <!-- Specify more shortcuts here. -->
</shortcuts>
```
相当直截了当，在示例中，我使用自定义action，以便检查在Activity中检查intent("com.your.app.QUICKSTART")。

接着我们需要在AndroidManifest中添加这个新xml文件的引用。只需要在主Activity的intent-filter之后添加。

```
<meta-data android:name="android.app.shortcuts"
    android:resource="@xml/shortcuts" />
```

现在处理快捷方式。在Activity中，为自定义intent action添加一个常量。

```
private static final String ACTION_QUICKSTART = "com.your.app.QUICKSTART";
```

在onCreate方法中，检查自定义intent action，增加你的处理...

```
if (ACTION_QUICKSTART.equals(getIntent().getAction())){
    startQuickStart();
}
```

嘿，一个简单的应用程序的快捷方式。

![](https://cdn-images-1.medium.com/max/1600/1*FocYpVdQSIWfPuk2vbNJvQ.png)
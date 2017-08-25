## Kotlin Data Class

Kotlin源码，简单的`Student.kt`类

```kotlin
data class Student(val name: String, val age: Int?= null)
```

使用命令`javap -c Student.class`反解析class文件，得到`Student.class`的编译的代码。

```kotlin
Compiled from "Student.kt"
public final class Student {
  public final java.lang.String getName();//生成的获取name的函数

  public final java.lang.Integer getAge();//生成的获取age的函数
  
  public Student(java.lang.String, java.lang.Integer);//初始化函数
    Code:
       0: aload_1
       1: ldc           #23                 // String name
       3: invokestatic  #29                 // Method kotlin/jvm/internal/Intrinsics.checkParameterIsNotNull:(Ljava/lang/Object;Ljava/lang/String;)V
       6: aload_0
       7: invokespecial #32                 // Method java/lang/Object."<init>":()V
      10: aload_0
      11: aload_1
      12: putfield      #11                 // Field name:Ljava/lang/String;
      15: aload_0
      16: aload_2
      17: putfield      #20                 // Field age:Ljava/lang/Integer;
      20: return

  public Student(java.lang.String, java.lang.Integer, int, kotlin.jvm.internal.DefaultConstructorMarker);//默认构造函数
    Code:
       0: iload_3
       1: iconst_2
       2: iand
       3: ifeq          11
       6: aconst_null
       7: checkcast     #35                 // class java/lang/Integer
      10: astore_2
      11: aload_0
      12: aload_1
      13: aload_2
      14: invokespecial #37                 // Method "<init>":(Ljava/lang/String;Ljava/lang/Integer;)V
      17: return

  public final java.lang.String component1();//从Code里看出这是获取name的，但是为啥有这个函数呢？
    Code:
       0: aload_0
       1: getfield      #11                 // Field name:Ljava/lang/String;
       4: areturn

  public final java.lang.Integer component2();//从Code里看出这是获取age的，但是为啥有这个函数呢？
    Code:
       0: aload_0
       1: getfield      #20                 // Field age:Ljava/lang/Integer;
       4: areturn

  public final Student copy(java.lang.String, java.lang.Integer);

  public static Student copy$default(Student, java.lang.String, java.lang.Integer, int, java.lang.Object);

  public java.lang.String toString();
  ...

  public int hashCode();
  ...

  public boolean equals(java.lang.Object);
  ...
}
```

修改`Student.kt`，增加sex域，同时提供默认值

```kotlin
data class Student(val name: String, var age: Int?= null, val sex: String = "Male")
```

反编译的代码，对于

```kotlin
Compiled from "Student.kt"
public final class Student {
  public final java.lang.String getName();

  public final java.lang.Integer getAge();

  public final void setAge(java.lang.Integer);

  public final java.lang.String getSex();

  public Student(java.lang.String, java.lang.Integer, java.lang.String);
    Code:
       0: aload_1
       1: ldc           #30                 // String name
       3: invokestatic  #36                 // Method kotlin/jvm/internal/Intrinsics.checkParameterIsNotNull:(Ljava/lang/Object;Ljava/lang/String;)V//内部检查name域是否为null
       6: aload_3
       7: ldc           #37                 // String sex
       9: invokestatic  #36                 // Method kotlin/jvm/internal/Intrinsics.checkParameterIsNotNull:(Ljava/lang/Object;Ljava/lang/String;)V//内部检查sex域是否为null
      12: aload_0
      13: invokespecial #40                 // Method java/lang/Object."<init>":()V
      16: aload_0
      17: aload_1
      18: putfield      #11                 // Field name:Ljava/lang/String;
      21: aload_0
      22: aload_2
      23: putfield      #20                 // Field age:Ljava/lang/Integer;
      26: aload_0
      27: aload_3
      28: putfield      #27                 // Field sex:Ljava/lang/String;
      31: return

  public Student(java.lang.String, java.lang.Integer, java.lang.String, int, kotlin.jvm.internal.DefaultConstructorMarker);
    Code:
       0: iload         4
       2: iconst_2
       3: iand
       4: ifeq          12
       7: aconst_null
       8: checkcast     #43                 // class java/lang/Integer
      11: astore_2
      12: iload         4
      14: iconst_4
      15: iand
      16: ifeq          22
      19: ldc           #45                 // String Male //sex域的默认值
      21: astore_3
      22: aload_0
      23: aload_1
      24: aload_2
      25: aload_3
      26: invokespecial #47                 // Method "<init>":(Ljava/lang/String;Ljava/lang/Integer;Ljava/lang/String;)V
      29: return

  public final java.lang.String component1();
    Code:
       0: aload_0
       1: getfield      #11                 // Field name:Ljava/lang/String;
       4: areturn

  public final java.lang.Integer component2();
    Code:
       0: aload_0
       1: getfield      #20                 // Field age:Ljava/lang/Integer;
       4: areturn

  public final java.lang.String component3();
    Code:
       0: aload_0
       1: getfield      #27                 // Field sex:Ljava/lang/String;
       4: areturn

  public final Student copy(java.lang.String, java.lang.Integer, java.lang.String);

  public static Student copy$default(Student, java.lang.String, java.lang.Integer, java.lang.String, int, java.lang.Object);

  public java.lang.String toString();

  public int hashCode();

  public boolean equals(java.lang.Object);
}
```
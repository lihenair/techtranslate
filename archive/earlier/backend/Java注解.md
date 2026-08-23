##Java注解

- Java注解的目的
- 注解基础
  - 注解元素
- 注解部署
- 内置Java注解
  - @Override
  - @SuppressWarnings
- 定制注解
 - @Retention
 - @Target
 - @Inherited
 - @Documented

Java注解用于向代码提供元数据。作为元数据，Java注解不直接影响代码执行，尽管有些注解类型可以用于这个目的。
Java注解从Java 5引入。包含Java注解的代码在Java 6中仍然没有改变。就我所知，Java注解在Java 7中也没有改变，所以Java 7中仍然可以继续使用注解。

####Java注解目的

Java注解通常用于如下目的：

- 编译器指令
- 内置指令
- 运行时指令

Java有3个内置注解可以向Java编译器设置指令。这3个注解将在后面展开。

Java注解可以用于构建，当构建软件工程时。构建过程包括生成源码，编译代码，生成XML文档(例如，部署描述符)，打包编译的代码和生成JAR文件等等。构建软件通常使用自动化构建工具例如Apache Ant或者Apache Maven。构建工具可能会扫描指定标注的Java代码并生成源码或其他基于这些注解的其他文档。

正常来说，Java注解编译后不会出现在代码中。然而可以定制注解在执行时可用。这些注解可以通过Java反射访问，用来向程序或第三方API提供指令。

####注解基础

Java注解可以包含元素，这些元素可以设置。元素类似属性或参数。这是一个待元素的Java注解：

 `@Entity(tableName = "vehicles")`

例子中的注解包含单一元素名为tableName，赋值为vehicles。元素包含在注解名后面的括号中。不带元素的注解不需要括号。

注解可以包含多个元素。多元素Java注解例子如下：

 `@Entity(tableName = "vehicles", primaryKey = "id")`

包含一个元素的注解，可以转化元素名为value，例如：

`@InsertNew(value = "yes")`

当注解只包含一个名为value的元素时，可以忽略元素名，只提供值。仅有一个值的注解例子如下：

`@InsertNew("yes")`

####注解放置

可以把Java注解放在类，接口，方法，方法参数，域和本地变量上。增加注解到类定义上：

`@Entity
public class Vehicle {
}`


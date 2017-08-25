# 深入字节码操作：使用ASM和Javassist创建审核日志

原文链接:[https://blog.newrelic.com/2014/09/29/diving-bytecode-manipulation-creating-audit-log-asm-javassist/](https://blog.newrelic.com/2014/09/29/diving-bytecode-manipulation-creating-audit-log-asm-javassist/)

在堆栈中使用Spring和Hibernate，您的应用程序的字节码可能会在运行时被增强或处理。 字节码是Java虚拟机（JVM）的指令集，所有在JVM上运行的语言都必须最终编译为字节码。 操作字节码原因如下：

* 程序分析:
	* 查找应用bug
	* 检查代码复杂性
	* 查找特定注解的类
* 类生成:
	* 使用代理从数据库中懒惰加载数据
* 安全性
	* 特定API限制访问权限
	* 代码混淆
* 无Java源码类转换
	* 代码分析
	* 代码优化
* 最后，添加日志

有几种可用于操作字节码的工具，从非常低级的工具（如需要字节码级别工作的ASM）到诸如AspectJ等高级框架（允许编写纯Java）。 

![](http://blog.newrelic.com/wp-content/uploads/BM1.png)

本博文，我将演示分别使用Javassist和ASM实现一种审计日志的方法。

### 审计日志例子
假定我没有如下代码：

```java
public class BankTransactions {
    public static void main(String[] args) {
	BankTransactions bank = new BankTransactions();
	for (int i = 0; i < 100; i++) {
	    String accountId = "account" + i;
	    bank.login("password", accountId, "Ashley");
	    bank.unimportantProcessing(accountId);
	    bank.withdraw(accountId, Double.valueOf(i));
	}
	System.out.println("Transactions completed");
    }
}
```
我们要记录重要的操作以及关键信息以确定操作。 以上，我将确定*登录*退出的重要动作。 对于登录，重要信息将是帐户ID和用户。 对于退出，重要信息将是*帐户ID*和撤回的金额。 记录重要操作的一种方法是将日志记录语句添加到每个重要的方法，但这将是乏味的。 相反，我们可以为重要的方法添加注释，然后使用工具来注入日志记录。 在这种情况下，该工具将是一个字节码操作框架。

```java
@ImportantLog(fields = { "1", "2" })
public void login(String password, String accountId, String userName) {
    // login logic
}
@ImportantLog(fields = { "0", "1" })
public void withdraw(String accountId, Double moneyToRemove) {
    // transaction logic
}
```

`@ImportantLog`注释表示我们要在每次调用该方法时记录一条消息，而`@ImportantLog`注释中的fields参数表示应记录的每个参数的索引位置。 例如，对于登录，我们要记录第1位和第2位的输入参数。它们是*accountId*和*userName*。 我们不会记录第0位的密码参数。

使用字节码和注释来执行日志记录有两个主要优点：

1. 日志记录与业务逻辑分离，这有助于保持代码清洁和简单。
2. 在不修改源代码的情况下，轻松删除审核日志记录。

### 在哪里实际修改字节码？
我们可以使用1.5中引入的核心Java功能来操纵字节码。 此功能称为[Java代理](http://docs.oracle.com/javase/8/docs/api/java/lang/instrument/package-summary.html)。
要了解Java代理，让我们来看一下典型的Java处理流程。

![](http://blog.newrelic.com/wp-content/uploads/BM2.png)

使用包含我们的main方法的类作为输入参数执行命令`java`。 这将启动Java运行时环境，使用`classloader`来加载输入类，并调用该类的main方法。 在我们具体的例子中，调用了`BankTransactions`的main方法，这将导致一些处理发生，并打印“完成交易”。

现在来看一下使用Java代理的Java进程。

![](http://blog.newrelic.com/wp-content/uploads/BM3.png)

命令`java`运行两个输入参数。第一个是JVM参数-`javaagent`，指向代理jar。第二个是包含我们主要方法的类。*javaagent*标志告诉JVM首先加载代理。 代理的主类必须在代理jar的清单中指定。 一旦类被加载，类的premain方法被调用。 这个premain方法充当代理的安装钩子。 它允许代理注册一个*类变换器*。 当类变换器在JVM中注册时，该变换器将在类加载到JVM前接收每个类的字节。 这为类变换器提供了根据需要修改类的字节的机会。 一旦类变换器修改了字节，它将修改的字节返回给JVM。 这些字节接着由JVM验证和加载。

在我们具体的例子中，当`BankTransaction`加载时，字节将首先进入类变换器进行潜在的修改。修改后的字节将被返回并加载到JVM中。 加载完之后，调用类中的main方法，进行一些处理，并打印“事务完成”。

让我们来看看代码。 下面我有代理的premain方法：

```java
public class JavassistAgent {
    public static void premain(String agentArgs, Instrumentation inst) {
	System.out.println("Starting the agent");
	inst.addTransformer(new ImportantLogClassTransformer());
    }
}
```

premain方法打印出一个消息，然后注册一个类变换器。 类变换器必须实现方法转换，加载到JVM中的每个类都会调用它。它以该类的字节数组作为方法的输入，然后返回修改后的字节数组。如果类变换器决定不修改特定类的字节，则可以返回null。

```java
public class ImportantLogClassTransformer implements ClassFileTransformer {
    public byte[] transform(ClassLoader loader, String className,
	Class classBeingRedefined, ProtectionDomain protectionDomain,
	byte[] classfileBuffer) throws IllegalClassFormatException {
	// manipulate the bytes here
        return modified bytes;
    }
}
```

现在我们知道在哪里修改一个类的字节，接着需要知道如何修改字节。

### 如何使用Javassist修改字节码？
[Javassist](http://www.csg.ci.i.u-tokyo.ac.jp/~chiba/javassist/)是一个具有高级和低级API的字节码操作框架。我将重点关注高级的面向对象的API，首先从Javassist中的对象的解释开始。接下来，我将实现审核日志应用程序的实际代码。

![](http://blog.newrelic.com/wp-content/uploads/BM4.png)

Javassist使用*CtClass对象*来表示一个类。 这些CtClass对象可以从*ClassPool*获得，用于修改Classes。ClassPool是一个基于*HashMap*实现的CtClass对象容器，其中键是类名称，值是表示该类的CtClass对象。默认的ClassPool使用与底层JVM相同的类路径。因此，在某些情况下，可能需要向ClassPool添加类路径或类字节。

类似于包含字段，方法和构造函数的Java类，CtClass对象包含*CtFields*，*CtConstructors*和*CtMethods*。所有这些对象都可以修改。我将重点关注方法操作，因为审核日志应用程序需要这种行为。

以下是修改方法的几种方法：

![](http://blog.newrelic.com/wp-content/uploads/Javassist2.png)

上图显示了Javassist的主要优点之一。实际上不必写字节码。而是编写Java代码。一个复杂的情况是Java代码必须在引号内。

现在我们了解了Javassist的基本构建块，现在来看看应用程序的实际代码。 类变换器的变换方法需要执行以下步骤：

1. 将字节数组转换为CtClass对象
2. 检查CtClass中每个带注解`@ImportantLog`的方法
3. 如果方法中存在@ImportantLog注释，那么:
	* 获取方法重要参数索引
	* 函数开始增加日志语句

使用Javassist编写Java代码时，请注意以下问题：

* JVM在包之间使用斜杠，而Javassist使用点。
* 当插入多行Java代码时，代码需要在括号内。
* 当使用$1，$2等引用方法参数值时，知道$0被保留给“this”。这意味着您方法的第一个参数的值为$1。
* 注释拥有可见和不可见的签。 不可见的注释在运行时无法获取。

实际的Java代码如下：

```java
public class ImportantLogClassTransformer implements ClassFileTransformer {
  private static final String METHOD_ANNOTATION = 
      "com.example.spring2gx.mains.ImportantLog";
  private static final String ANNOTATION_ARRAY = "fields";
  private ClassPool pool;
                               
  public ImportantLogClassTransformer() {
    pool = ClassPool.getDefault();
  }
                     
  public byte[] transform(ClassLoader loader, String className,
    Class classBeingRedefined, ProtectionDomain protectionDomain,
    byte[] classfileBuffer) throws IllegalClassFormatException {
    try {
      pool.insertClassPath(new ByteArrayClassPath(className,
        classfileBuffer));
      CtClass cclass = pool.get(className.replaceAll("/", "."));
	if (!cclass.isFrozen()) {
	  for (CtMethod currentMethod : cclass.getDeclaredMethods()) {
	    Annotation annotation = getAnnotation(currentMethod);
	    if (annotation != null) {
	      List parameterIndexes = getParamIndexes(annotation);
		currentMethod.insertBefore(createJavaString(
		currentMethod, className, parameterIndexes));
	    }
	  }
	  return cclass.toBytecode();
	}
      } catch (Exception e) {
	e.printStackTrace();
      }
      return null;
    }
                        
  private Annotation getAnnotation(CtMethod method) {
    MethodInfo mInfo = method.getMethodInfo();
    // the attribute we are looking for is a runtime invisible attribute
    // use Retention(RetentionPolicy.RUNTIME) on the annotation to make it
    // visible at runtime
    AnnotationsAttribute attInfo = (AnnotationsAttribute) mInfo
      .getAttribute(AnnotationsAttribute.invisibleTag);
    if (attInfo != null) {
      // this is the type name meaning use dots instead of slashes
      return attInfo.getAnnotation(METHOD_ANNOTATION);
    }
    return null;
  }
                       
  private List getParamIndexes(Annotation annotation) {
    ArrayMemberValue fields = (ArrayMemberValue) annotation
      .getMemberValue(ANNOTATION_ARRAY);
    if (fields != null) {
      MemberValue[] values = (MemberValue[]) fields.getValue();
      List parameterIndexes = new ArrayList();
      for (MemberValue val : values) {
	parameterIndexes.add(((StringMemberValue) val).getValue());
      }
      return parameterIndexes;
    }
    return Collections.emptyList();
  }
                            
  private String createJavaString(CtMethod currentMethod, String className,
    List indexParameters) {
    StringBuilder sb = new StringBuilder();
    sb.append("{StringBuilder sb = new StringBuilder");
    sb.append("(\"A call was made to method '\");");
    sb.append("sb.append(\"");
    sb.append(currentMethod.getName());
    sb.append("\");sb.append(\"' on class '\");");
    sb.append("sb.append(\"");
    sb.append(className);
    sb.append("\");sb.append(\"'.\");");
    sb.append("sb.append(\"\\n    Important params:\");");
    for (String index : indexParameters) {
      try {
	// add one because 0 is "this" for instance variable
	// if were a static method 0 would not be anything
	int localVar = Integer.parseInt(index) + 1;
	sb.append("sb.append(\"\\n        Index \");");
	sb.append("sb.append(\"");
	sb.append(index);
	sb.append("\");sb.append(\" value: \");");
	sb.append("sb.append($" + localVar + ");");
      } catch (NumberFormatException e) {
	e.printStackTrace();
      }
    }
    sb.append("System.out.println(sb.toString());}");
    return sb.toString();
  }
}
```
完成了！我们可以运行应用程序，并将日志记录输出到“System.out”。

积极的一面是写入的代码量非常小，而且实际上不需要使用Javassist编写字节码。 最大的缺点是用引号编写Java代码可能会变得乏味。幸运的是，其他一些字节码操作框架更快。我们来看看其中一个更快的框架。

### 如何使用ASM修改字节？
[ASM](http://asm.ow2.org/)是一个字节码操作框架，使用较小的内存占用并且速度相对较快。我认为ASM是字节码操作的行业标准，即使是Javassist也在使用ASM。ASM提供基于对象和事件的库，但在这里我将重点介绍基于事件的模型。

要理解ASM，我将从ASM自己的文档的一个Java类图(下图)开始。它表明Java类由几个部分组成，包括一个超类，接口，注释，字段和方法。在ASM基于事件的模型中，所有这些类组件都可以被认为是事件。

![](http://blog.newrelic.com/wp-content/uploads/BM5.png)

可以在*ClassVisitor*上找到ASM的类事件。为了“看到”这些事件，必须创建一个classVisitor来覆盖您想要查看的所需组件。

![](http://blog.newrelic.com/wp-content/uploads/BM6.png)

除了类访问者，我们需要一些东西来解析类并生成事件。为此，ASM提供了一个名为*ClassReader*的对象。reader解析课程并产生事件。类被解析后，需要*ClassWriter*来消耗事件，将它们转换成一个类字节数组。在下图中，我们`BankTransactions`类的字节传递给ClassReader，该字节将字节发送到ClassWriter，该ClassWriter会输出生成的BankTransaction。当没有ClassVisitor存在时，输入BankTransactions字节应基本上匹配其输出字节。

![](http://blog.newrelic.com/wp-content/uploads/BM9.png)

```java
public byte[] transform(ClassLoader loader, String className,
    Class<?> classBeingRedefined, ProtectionDomain protectionDomain,
    byte[] classfileBuffer) throws IllegalClassFormatException {
                                  
    ClassReader cr = new ClassReader(classfileBuffer);
    ClassWriter cw = new ClassWriter(cr, ClassWriter.COMPUTE_FRAMES);
    cr.accept(cw, 0);
    return cw.toByteArray();
}
```

ClassReader得到类的字节，ClassWriter从类读取器获取。ClassReader的`accept`调用解析该类。接下来，我们从ClassWriter访问生成的字节。

现在我们想修改BankTransaction字节。首先，我们需要链接在ClassVisitor中。 此ClassVisitor将覆盖诸如`visitField`或`visitMethod`之类的方法来接收关于该特定类组件的通知。

![](http://blog.newrelic.com/wp-content/uploads/BM7.png)

以下是上图的代码实现。 类访问者`LogMethodClassVisitor`已添加。请注意，可以添加多个类访问者。

```java
public byte[] transform(ClassLoader loader, String className,
    Class<?> classBeingRedefined, ProtectionDomain protectionDomain,
    byte[] classfileBuffer) throws IllegalClassFormatException {
                            
    ClassReader cr = new ClassReader(classfileBuffer);
    ClassWriter cw = new ClassWriter(cr, ClassWriter.COMPUTE_FRAMES);
    ClassVisitor cv = new LogMethodClassVisitor(cw, className);
    cr.accept(cv, 0);
    return cw.toByteArray();
}
```
对于审核日志应用，我们需要检查类中的每个方法。这意味着ClassVisitor只需要覆盖'visitMethod'。

```java
public class LogMethodClassVisitor extends ClassVisitor {
    private String className;
           
    public LogMethodClassVisitor(ClassVisitor cv, String pClassName) {
	super(Opcodes.ASM5, cv);
	className = pClassName;
    }
                                                         
    @Override
    public MethodVisitor visitMethod(int access, String name, String desc,
	    String signature, String[] exceptions) {
	//put logic in here
    }
}
```

请注意，`visitMethod`返回一个*MethodVisitor*。 就像一个类有多个组件，一个方法也有很多的组件，当解析该方法时，它可以被认为是事件。

![](http://blog.newrelic.com/wp-content/uploads/BM8.png)

MethodVisitor在方法上提供事件。对于审核日志应用，我们要检查带注释的方法上。基于注释，我们可能需要修改方法中的实际代码。为了进行这些修改，我们需要在一个`methodVisitor`链接，如下所示。

```java
@Override
public MethodVisitor visitMethod(int access, String name, String desc, 
    String signature, String[] exceptions) {                               
    MethodVisitor mv = super.visitMethod(access, name, desc, signature,
            exceptions);
    return new PrintMessageMethodVisitor(mv, name, className);
}
```

这个`PrintMessageMethodVisitor`将需要覆盖`visitAnnotation`和`visitCode`。请注意，`visitAnnotation`返回一个*AnnotationVisitor*。就像类和方法具有组件一样，还有一个注释的多个组件。AnnotationVisitor允许我们访问注释的所有部分。

下面我简要介绍了visitAnnotation和visitCode的步骤。

```java
public class PrintMessageMethodVisitor extends MethodVisitor {
  @Override
  public AnnotationVisitor visitAnnotation(String desc, boolean visible) {
    // 1. check method for annotation @ImportantLog
    // 2. if annotation present, then get important method param indexes
  }
                                                     
  @Override
  public void visitCode() {
    // 3. if annotation present, add logging to beginning of the method
  }	
}
```
当使用ASM编写Java代码时，请注意以下问题：

* 在事件模型中，类或方法的事件将始终以特定顺序发生。 例如，带注解的方法将始终在实际代码之前访问。
* 当使用$1，$2等引用方法参数值时，知道$0被保留用于“this”。这意味着您方法的第一个参数的值为$1。

实际Java代码如下：

```java
public AnnotationVisitor visitAnnotation(String desc, boolean visible) {
  if ("Lcom/example/spring2gx/mains/ImportantLog;".equals(desc)) {
    isAnnotationPresent = true;
    return new AnnotationVisitor(Opcodes.ASM5,
        super.visitAnnotation(desc, visible)) {
      public AnnotationVisitor visitArray(String name, Object value) {
        if ("fields".equals(name)) {
          return new AnnotationVisitor(Opscodes.ASM5,
              super.visitArray(name)) { 
            public void visit(String name, Object value) {
              parameterIndexes.add((String) value);
              super.visit(name, value);
            }
          };
        } else {
          return super.visitArray(name);
        }
      }
    };
  }
  return super.visitAnnotation(desc, visible);
}                                                                                                                       
public void visitCode() {
  if (isAnnotationPresent) {
    // create string builder
    mv.visitFieldInsn(Opcodes.GETSTATIC, "java/lang/System", 
        "out","Ljava/io/PrintStream;");
    mv.visitTypeInsn(Opcodes.NEW, "java/lang/StringBuilder");
    mv.visitInsn(Opcodes.DUP);
    // add everything to the string builder
    mv.visitLdcInsn("A call was made to method \"");
    mv.visitMethodInsn(Opcodes.INVOKESPECIAL,
        "java/lang/StringBuilder", "",
        "(Ljava/lang/String;)V", false);
    mv.visitLdcInsn(methodName);
    mv.visitMethodInsn(Opcodes.INVOKEVIRTUAL,
        "java/lang/StringBuilder", "append",
        "(Ljava/lang/String;)Ljava/lang/StringBuilder;", false);
. . .
```
以上可以看出Javassist和ASM之间的主要区别之一。使用ASM，必须在修改方法时在字节码级别编写代码，这意味着需要很好地了解JVM的工作原理。需要在给定的时刻确切知道堆栈和局部变量的内容。 在字节码级别的编写方面，在功能和优化方面提高了门槛，这意味着开发人员需要较长的时间熟悉ASM开发。

### 家庭作业
现在你已经看到如何使用ASM和Javassist的一个场景，我鼓励你尝试一个字节码操作框架。字节码操作不仅可以让您更好地了解JVM，而且还有无数的应用程序。一旦开始，你会发现天空的极限。
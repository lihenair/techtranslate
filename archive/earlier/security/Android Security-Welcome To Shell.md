# Android安全性：欢迎来到Shell(权限)

原文链接：[http://doridori.github.io/Android-Security-welcome-to-shell/#sthash.su8mxX38.dpbs](http://doridori.github.io/Android-Security-welcome-to-shell/#sthash.su8mxX38.dpbs)

从应用启动与从`adb`启动shell有相同的权限么？多好的一个问题啊！

> *ADB是一个在PC上运行shell，就像你在手机上执行shell/terminal应用一样有相同的权限*

我在Reddit上看到[这句话](https://www.reddit.com/r/computerforensics/comments/4xrz86/forensics_tool_nabs_data_from_signal_telegram/d6ir97g)，它跟我的直觉相反，所以我赶紧查查。对我重要的是我可以理解围绕着shell潜在攻击载体的不同。

我开始浏览[Android内部安全性:深入了解Android安全架构](https://www.amazon.co.uk/Android-Security-Internals-Depth-Architecture/dp/1593275811)来得到关于进程权限在Android上是如何工作的概述。大部分的概述是这本大书中几页的精华版。

本文大部分讨论这些东西与底层内核权限的工作是如何在OS中运行的，而不涉及包管理器(pm)的高级操作。

### 底层事物简述

* 特权是基于进程的[UID](https://en.wikipedia.org/wiki/User_identifier)，[GID](https://en.wikipedia.org/wiki/Group_identifier)和附加GID
* 像所有POSIX系统[需要澄清]访问内核监控的系统资源是基于所有者和资源访问模式和访问进程的UID和GID
* Android的一些权限映射到GID的[data/etc/platform.xml](https://android.googlesource.com/platform/frameworks/base/+/master/data/etc/platform.xml)
  * 其他权限由`pm`检查，我猜测进程不可检查超出这本文的范围
* 这些GID对应[android_filesystem_config.h](https://android.googlesource.com/platform/system/core/+/master/include/private/android_filesystem_config.h)中的AID
* 对于应用(快速讲述)包管理器分别在应用安装时，`platform.xml`中的权限以及`data/system/packages.list`的应用入口添加GID
* UID和GID在进程从*zygote*进程fork时设置，因为它生成新的应用进程。内核和系统守护进程使用这些值来保证资源和功能的访问

### 相对的Shell权限
那么，从应用启动的shell与从`adb`有相同的权限么？让我们看看。
启动一个`adb shell`，通过剪切`ps`的输出，我们可以看到父进程树：

```
#ps
USER      PID   PPID  VSIZE  RSS   WCHAN              PC  NAME
root      1     0     4524   908   SyS_epoll_ 0000000000 S /init
shell     503   1     9952   700              0000000000 S /sbin/adbd
shell     17432 29176 5744   1156           0 7f8b5d6c7c R ps
shell     29176 503   5800   1444  sigsuspend 7f9663f37c S /system/bin/sh
```
使用它来查看用户shell的GID：

```
shell@angler:/ $ cat /proc/$$/status                                           
Name:   sh
State:  R (running)
Tgid:   29176
Pid:    29176
PPid:   503
TracerPid:  0
Uid:    2000    2000    2000    2000
Gid:    2000    2000    2000    2000
FDSize: 64
Groups: 1004 1007 1011 1015 1028 3001 3002 3003 3006  //GIDs
VmPeak:     5800 kB
VmSize:     5800 kB
VmLck:         0 kB
VmPin:         0 kB
VmHWM:      1440 kB
VmRSS:      1440 kB
VmData:     2956 kB
VmStk:       136 kB
VmExe:       276 kB
VmLib:      2068 kB
VmPTE:        24 kB
VmSwap:        0 kB
Threads:    1
SigQ:   0/9445
SigPnd: 0000000000000000
ShdPnd: 0000000000000000
SigBlk: 0000000000000000
SigIgn: 0000000000380000
SigCgt: 000000000801f4ff
CapInh: 0000000000000000
CapPrm: 0000000000000000
CapEff: 0000000000000000
CapBnd: 00000000000000c0
Seccomp:    0
Cpus_allowed:   ff
Cpus_allowed_list:  0-7
Mems_allowed:   1
Mems_allowed_list:  0
voluntary_ctxt_switches:    163
nonvoluntary_ctxt_switches: 69
```
你可以与已安装应用中调用的shell命令进行比较。由于`Runtime.exec()`的怪癖，我发现可以从已安装应用中通过发送一条缓慢的shell命令(`sleep 100`)并检查我已打开的`adb shell`。下面如预期的，我们看到了完全不同的PPID树：

```
#ps
USER      PID   PPID  VSIZE  RSS   WCHAN              PC  NAME
root      1     0     4524   908   SyS_epoll_ 0000000000 S /init
root      527   1     2098548 62336 poll_sched 0000000000 S zygote64
u0_a89    13493 527   1457592 57276  pipe_wait 0000000000 S com.mypinpad.shellpermstest
u0_a89    13515 13493 5920   1164  hrtimer_na 0000000000 S sleep
```
查询GID得到：

```
shell@angler:/ $ cat /proc/13515/status                                        
Name:   sleep
State:  S (sleeping)
Tgid:   13515
Pid:    13515
PPid:   13493
TracerPid:  0
Uid:    10089   10089   10089   10089
Gid:    10089   10089   10089   10089
FDSize: 64
Groups: 9997 50089 
VmPeak:     5920 kB
VmSize:     5920 kB
VmLck:         0 kB
VmPin:         0 kB
VmHWM:      1164 kB
VmRSS:      1164 kB
VmData:     2716 kB
VmStk:       136 kB
VmExe:       292 kB
VmLib:      2376 kB
VmPTE:        24 kB
VmSwap:        0 kB
Threads:    1
SigQ:   0/9445
SigPnd: 0000000000000000
ShdPnd: 0000000000000000
SigBlk: 0000000000001204
SigIgn: 0000000000001000
SigCgt: 00000000000084f8
CapInh: 0000000000000000
CapPrm: 0000000000000000
CapEff: 0000000000000000
CapBnd: 0000000000000000
Seccomp:    0
Cpus_allowed:   ff
Cpus_allowed_list:  0-7
Mems_allowed:   1
Mems_allowed_list:  0
voluntary_ctxt_switches:    2
nonvoluntary_ctxt_switches: 6
```
`10089`是发出shell命令的应用的UID。
从上面的比较，我们可以看到GID权限实际上是不相同的，而且用户也是不同的！
一个显著的例子是`adb shell`有3003的GID，定义是`#define AID_INET 3003 /* can create AF_INET and AF_INET6 sockets */`，所以默认它自带`INTERNET`权限。

### 深入研究
可能知道`shell`用户访问的系统资源是有趣的。我想在root/模拟器设备上执行一条简单命令就可以知道。

*编辑：[还应该从CopperheadOS看看](https://twitter.com/CopperheadOS/status/766363947066941441)*

### 结论
一句话，是的。一个打开的shell的权限取决于它的进程所有者和组。启动shell的依赖可以是不同的。

我发现探究内核权限是有趣的(一句我从没想说的话！)，所以我也有同感。如果你看到任何不正确的，请联系我。

如果你发现这个很有趣，你可能喜欢[doridori/Android-Security-Reference](https://github.com/doridori/Android-Security-Reference).

### 附录：ro.*
旁注。根据ADB(Android调试桥)：它是怎么工作的？如果系统属性`ro.secure = 1`(因为所有OEM设备都是这个值)，那么`adbd`就作为`shell`运行，否则，它就是`root`用户，例如，像模拟器那样，也可能是已分散的开发设备。

这个应用会以root用户执行`adbd`。我假设临时设置了`ro.secure`并重启了`adbd`。

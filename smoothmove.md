##平滑移动分析
- Model
- Push
- Marker
- Animation

###Model
* NearDriver 周边司机对象数组
* Driver     司机对象

###Push
需要注册Push消息。kPushMessageTypeGulfstreamPassengerDriverLocReq和kPushMessageTypeGulfstreamPassengerDriverLocByIdsReq

- kPushMessageTypeGulfstreamPassengerDriverLocByReq
> 用于在实时界面显示当前附近车辆。消息会带来周边司机的信息。
> 每次传递10个司机的坐标信息。

- kPushMessageTypeGulfstreamPassengerDriverLocByIdsReq
> 用于等待接驾页面显示司机行驶状态。
> 每次传递一个司机的坐标数组。

###Marker
需要一个并发保存的司机图标Map，保存司机信息和司机ID。初始时该map为空，会加载出发地位置的周边司机到地图上。如果map非空，则根据传入的司机信息数据逐个比较当前的map，用于更新周边司机的信息。
###Animation
Marker涉及到的动画包括旋转和移动两种。需要引入tencentmap的动画支持**AnimationSet,RotateAnimation,TranslateAnimation**。

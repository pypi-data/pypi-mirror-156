## xlinjietool
- 打造集成工具库
---
### 总览
- amazon(亚马逊解析)
- db(数据库)
- headers(header头解析)
#### amazon(亚马逊解析)
> 各个站点日期解析<br>
> 站点链接组装<br>
#### db(数据库)
> es<br>
> redis<br>
> mysql<br>
#### headers(header头解析)
> 把web复制的headers解析成为json

---
#### 时间相关
```python
from xlj.Comm import Time

print(Time.timestamp_to_time())
print(Time.timestamp_to_time(16563153))
print(Time.timestamp_to_time(1656315389))
print(Time.timestamp_to_time('1656315389'))
print(Time.now_timestamp())
print(Time.now_timestamp(10))
2022-06-27 15:37:49
2022-06-27 15:35:00
2022-06-27 15:36:29
2022-06-27 15:36:29
1656315469353
1656315469
```
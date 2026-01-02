from datetime import datetime, date


def _parse_date_input(date_input):
    """解析日期输入为 date 对象
    
    Args:
        date_input: 支持多种格式:
            - date 对象
            - datetime 对象(会提取日期部分)
            - 字符串格式1: "2026:01:01" (只有日期)
            - 字符串格式2: "2026:01:01 20:33:12" (完整时间)
            - 字符串格式3: "2026-01-01" (ISO格式)
        
    Returns:
        date 对象
    """
    if isinstance(date_input, date) and not isinstance(date_input, datetime):
        return date_input
    elif isinstance(date_input, datetime):
        return date_input.date()
    elif isinstance(date_input, str):
        # 尝试不同的格式
        for fmt in ["%Y:%m:%d %H:%M:%S", "%Y:%m:%d", "%Y-%m-%d"]:
            try:
                dt = datetime.strptime(date_input, fmt)
                return dt.date()
            except ValueError:
                continue
        raise ValueError(f"无法解析日期字符串: {date_input}")
    else:
        raise TypeError(f"不支持的日期类型: {type(date_input)}")


def _get_item_date(item):
    """获取 item 的日期(只到天,不含时分秒)
    
    Args:
        item: OnlineItem 对象
        
    Returns:
        date 对象,如果没有 date_time 则返回 None
    """
    extra_info = item.info.get("extra_info", {})
    date_time_str = extra_info.get("date_time", None)
    if date_time_str:
        try:
            dt = datetime.strptime(date_time_str, "%Y:%m:%d %H:%M:%S")
            return dt.date()  # 只返回日期部分
        except ValueError:
            return None
    return None


def _binary_search_first_before_date(items, end_date):
    """二分查找第一个早于 end_date 的 item 的索引(按日期粒度)
    
    Args:
        items: item 列表(时间倒序,即最新的在前面)
        end_date: date 对象,结束日期
        
    Returns:
        第一个早于 end_date 的 item 的索引,如果没有找到则返回 -1
    """
    left, right = 0, len(items) - 1
    result = -1
    
    while left <= right:
        mid = (left + right) // 2
        mid_date = _get_item_date(items[mid])
        
        if mid_date is None:
            # 如果当前 item 没有日期信息,跳过
            left = mid + 1
            continue
        
        if mid_date < end_date:
            # 当前 item 的日期早于 end_date,记录位置并继续向左查找
            result = mid
            right = mid - 1
        else:
            # 当前 item 的日期晚于或等于 end_date,向右查找
            left = mid + 1
    
    return result


def get_photo_with_end_date_and_count_items(SinglePageFunc, end_date, count):
    """根据结束日期和数量获取指定数量的 items (按日期粒度,不考虑具体时间)
        结束日期向前数count个
    
    Args:
        SinglePageFunc: 单页获取函数,接受 cursor 参数,返回 {'items':[], 'has_more':True/False, 'cursor'}
        end_date: 结束日期,支持多种格式:
            - date 对象
            - datetime 对象(会提取日期部分)
            - 字符串: "2026:01:01" 或 "2026:01:01 20:33:12" 或 "2026-01-01"
        count: int,需要获取的 item 数量
        
    Returns:
        list,包含指定数量的 items (所有 item 的日期都早于 end_date)
    """
    # ----------------------------------------------------------------
    # def SinglePageFunc(cursor=None) -> dict:
    #     return { 'items':[] , "has_more":True/False, "cursor"  }
    # ----------------------------------------------------------------
    # 解析结束日期
    end_date = _parse_date_input(end_date)
    
    cursor = None
    r = []
    
    while True:
        # 获取一页数据
        page = SinglePageFunc(cursor=cursor)
        items = page["items"]
        
        if not items:
            # 没有更多数据了
            break
        
        # 检查最后一个 item 的日期
        last_item_date = _get_item_date(items[-1])
        
        if last_item_date is None or last_item_date >= end_date:
            # 最后一个 item 的日期仍然晚于或等于 end_date
            # 继续请求下一页
            if page["has_more"]:
                cursor = page["cursor"]
            else:
                # 没有更多数据了
                break
        else:
            # 最后一个 item 的日期早于 end_date
            # 使用二分查找找到第一个早于 end_date 的 item
            first_index = _binary_search_first_before_date(items, end_date)
            
            if first_index != -1:
                # 找到了第一个日期早于 end_date 的 item
                # 将从该位置开始的所有 items 加入结果
                r.extend(items[first_index:])
                
                # 检查是否已经收集到足够的数量
                if len(r) >= count:
                    return r[:count]
                
                # 如果还需要更多,继续请求
                if page["has_more"]:
                    cursor = page["cursor"]
                else:
                    break
            else:
                # 没有找到早于 end_date 的 item,继续下一页
                if page["has_more"]:
                    cursor = page["cursor"]
                else:
                    break
    
    # 返回收集到的所有 items(可能少于 count)
    return r[:count] if len(r) >= count else r


def _binary_search_date_range_boundary(items, start_date, end_date):
    """在items中找到日期区间的边界索引
    
    Args:
        items: item 列表(时间倒序,即最新的在前面)
        start_date: date 对象,开始日期(包含)
        end_date: date 对象,结束日期(不包含)
        
    Returns:
        tuple (start_index, end_index):
            - start_index: 第一个日期 >= start_date 的item索引,-1表示未找到
            - end_index: 第一个日期 < end_date 的item索引,-1表示未找到
    """
    # 找到第一个日期早于 end_date 的位置(即 < end_date)
    end_index = _binary_search_first_before_date(items, end_date)
    
    # 找到第一个日期早于 start_date 的位置
    # items在这个位置之前(不包含)的都是 >= start_date 的
    left, right = 0, len(items) - 1
    first_before_start = -1
    
    while left <= right:
        mid = (left + right) // 2
        mid_date = _get_item_date(items[mid])
        
        if mid_date is None:
            left = mid + 1
            continue
        
        if mid_date < start_date:
            # 找到第一个 < start_date 的位置
            first_before_start = mid
            right = mid - 1
        else:
            # mid_date >= start_date
            left = mid + 1
    
    # start_index 应该是从第一个item到 first_before_start 之前
    # 如果 first_before_start == -1,说明所有item的日期都 >= start_date
    # 如果 first_before_start == 0,说明第一个item就 < start_date,没有符合条件的
    
    if first_before_start == 0:
        # 第一个item就已经 < start_date,没有符合条件的items
        return -1, -1
    
    # 确定区间
    # [0, first_before_start) 是 >= start_date 的区间
    # [0, end_index] 是 < end_date 的区间
    # 交集就是 [0, min(first_before_start, end_index+1))
    
    if end_index == -1:
        # 没有 < end_date 的items,所有items都 >= end_date
        return -1, -1
    
    if first_before_start == -1:
        # 所有items都 >= start_date
        # 那么区间就是 [0, end_index]
        return 0, end_index
    else:
        # 区间是 [0, min(first_before_start-1, end_index)]
        if first_before_start - 1 < 0:
            return -1, -1
        return 0, min(first_before_start - 1, end_index)


def get_photo_with_date_range_items(SinglePageFunc, start_date, end_date):
    """获取指定日期区间内的所有 items (按日期粒度)
    
    Args:
        SinglePageFunc: 单页获取函数,接受 cursor 参数,返回 {'items':[], 'has_more':True/False, 'cursor'}
        start_date: 开始日期(包含),支持多种格式:
            - date 对象
            - datetime 对象(会提取日期部分)
            - 字符串: "2026:01:01" 或 "2026:01:01 20:33:12" 或 "2026-01-01"
        end_date: 结束日期(不包含),格式同 start_date
        
    Returns:
        list,包含日期在 [start_date, end_date) 区间内的所有 items
    """
    # ----------------------------------------------------------------
    # def SinglePageFunc(cursor=None) -> dict:
    #     return { 'items':[] , "has_more":True/False, "cursor"  }
    # ----------------------------------------------------------------
    # 解析日期
    start_date = _parse_date_input(start_date)
    end_date = _parse_date_input(end_date)
    
    if start_date >= end_date:
        raise ValueError(f"start_date ({start_date}) 必须小于 end_date ({end_date})")
    
    cursor = None
    r = []
    found_start_boundary = False
    
    while True:
        # 获取一页数据
        page = SinglePageFunc(cursor=cursor)
        items = page["items"]
        
        if not items:
            # 没有更多数据了
            break
        
        # 检查第一个 item 的日期(因为是倒序,第一个是最新的)
        first_item_date = _get_item_date(items[0])
        
        if first_item_date is not None and first_item_date < start_date:
            # 第一个item的日期都小于开始日期,说明已经超出范围,停止
            break
        
        # 检查最后一个 item 的日期
        last_item_date = _get_item_date(items[-1])
        
        # 判断当前页与区间的关系
        if last_item_date is not None and last_item_date >= end_date:
            # 整页都在 end_date 之后(或等于),继续请求下一页
            if page["has_more"]:
                cursor = page["cursor"]
            else:
                break
            continue
        
        # 到这里,说明当前页包含了部分或全部区间内的数据
        # 需要精确找到区间边界
        
        # 找到第一个 < end_date 的位置
        end_boundary = _binary_search_first_before_date(items, end_date)
        
        if end_boundary == -1:
            # 当前页没有 < end_date 的items,继续下一页
            if page["has_more"]:
                cursor = page["cursor"]
            else:
                break
            continue
        
        # 找到第一个 < start_date 的位置
        start_boundary = _binary_search_first_before_date(items, start_date)
        
        # 确定要收集的区间
        # start_boundary 是第一个 < start_date 的位置
        # [0, start_boundary) 是 >= start_date 的区间
        # [0, end_boundary] 是 < end_date 的区间
        # 交集是 [0, min(start_boundary if start_boundary != -1 else len(items), end_boundary+1))
        
        if start_boundary == -1:
            # 所有items都 >= start_date
            # 收集 [0, end_boundary]
            r.extend(items[0:end_boundary + 1])
            found_start_boundary = True
        elif start_boundary == 0:
            # 第一个item就 < start_date,没有符合条件的
            break
        else:
            # 收集 [0, min(start_boundary, end_boundary+1))
            collect_end = min(start_boundary, end_boundary + 1)
            r.extend(items[0:collect_end])
            found_start_boundary = True
            
            if start_boundary <= end_boundary:
                # 已经找到了 start_date 的边界,不需要继续
                break
        
        # 检查是否已经完整覆盖了区间
        if last_item_date is not None and last_item_date < start_date:
            # 已经超出 start_date,停止
            break
        
        # 继续下一页
        if page["has_more"]:
            cursor = page["cursor"]
        else:
            break
    
    return r


def get_photo_with_end_date_and_count(SinglePageFunc, end_date, count):
    """根据结束日期和数量获取指定数量的 items,返回标准数据格式
    
    这是 get_photo_with_end_date_and_count_items 的封装版本,
    返回与 api.get_self_1page 相同的数据结构
    
    Args:
        SinglePageFunc: 单页获取函数,接受 cursor 参数,返回 {'items':[], 'has_more':True/False, 'cursor'}
        end_date: 结束日期,支持多种格式:
            - date 对象
            - datetime 对象(会提取日期部分)
            - 字符串: "2026:01:01" 或 "2026:01:01 20:33:12" 或 "2026-01-01"
        count: int,需要获取的 item 数量
        
    Returns:
        dict: {'items': [...], 'has_more': False, 'cursor': None}
            - items: 包含指定数量的 items (所有 item 的日期都早于 end_date)
            - has_more: 总是 False (因为已经获取了所有需要的数据)
            - cursor: 总是 None
    """
    items = get_photo_with_end_date_and_count_items(SinglePageFunc, end_date, count)
    return {
        'items': items,
        'has_more': False,
        'cursor': None
    }


def get_photo_with_date_range(SinglePageFunc, start_date, end_date):
    """获取指定日期区间内的所有 items,返回标准数据格式
    
    这是 get_photo_with_date_range_items 的封装版本,
    返回与 api.get_self_1page 相同的数据结构
    
    Args:
        SinglePageFunc: 单页获取函数,接受 cursor 参数,返回 {'items':[], 'has_more':True/False, 'cursor'}
        start_date: 开始日期(包含),支持多种格式:
            - date 对象
            - datetime 对象(会提取日期部分)
            - 字符串: "2026:01:01" 或 "2026:01:01 20:33:12" 或 "2026-01-01"
        end_date: 结束日期(不包含),格式同 start_date
        
    Returns:
        dict: {'items': [...], 'has_more': False, 'cursor': None}
            - items: 包含日期在 [start_date, end_date) 区间内的所有 items
            - has_more: 总是 False (因为已经获取了所有需要的数据)
            - cursor: 总是 None
    """
    items = get_photo_with_date_range_items(SinglePageFunc, start_date, end_date)
    return {
        'items': items,
        'has_more': False,
        'cursor': None
    }

# atomic level
def get_idx(list, key):
    for idx in range(len(list)):
        if key == list[idx][0]:
            return idx


def ins(list, key, val):
    list.append([key, val])
    return list


def ret(list, key):
    idx = get_idx(list, key)
    return list[idx][1]


def upd(list, key, val):
    new_item = [key.lower(), val]
    idx = get_idx(list, key)
    list[idx] = new_item
    return list


def delete(list, key):
    idx = get_idx(list, key)
    list.remove(idx)
    return list


# table level
def ins_tab(db, table_name):
    return ins(db, table_name, [])


def ret_tab(db, table_name):
    return ret(db, table_name)


def upd_tab(db, table_name, table):
    return upd(db, table_name, table)


def del_tab(db, table_name):
    return delete(db, table_name)


# record level
def is_member(record, kv, check_value):
    if len(kv) == 0:
        return True
    else:
        for item in record:
            if item[0] == kv[0]:
                if check_value:
                    if item[1] == kv[1]:
                        return True
                else:
                    return True
        return False


def kvs_in_rec(record, kv_list):
    # all kv's of kv_list_search are members of record
    for kv in kv_list:
        if not is_member(record, kv, True):
            return False
    return True


def ins_rec(db, table_name, kv_list):
    table = ret(db, table_name)
    table.append(kv_list)
    return upd(db, table_name, table)


def ret_recs(db, table_name, kv_list):
    list = []
    table = ret(db, table_name)

    for record in table:
        if kvs_in_rec(record, kv_list):
            list.append(record)

    return list


def ret_rec_idx(db, table_name, record_idx):
    table = ret(db, table_name)
    if len(table) >= record_idx:
        return table[record_idx]
    else:
        return None


def upd_recs(db, table_name, kv_list_search, kv_list_upd):
    # updates all records identified by kv_list_search
    new_table = []
    old_table = ret_tab(db, table_name)

    for old_rec in old_table:
        if kvs_in_rec(old_rec, kv_list_search):
            # matching record
            new_rec = old_rec

            for kv in kv_list_upd:
                # if kv is member of record, update value of kv,
                # otherwise insert entire kv
                key = kv[0]
                val = kv[1]
                if is_member(new_rec, kv, False):
                    new_rec = upd(new_rec, key, val)
                else:
                    new_rec = ins(new_rec, key, val)

            new_table.append(new_rec)
        else:
            new_table.append(old_rec)

    return upd(db, table_name, new_table)


def del_recs(db, table_name, kv_list):
    new_table = []
    old_table = ret_tab(db, table_name)

    for record in old_table:
        if not kvs_in_rec(record, kv_list):
            new_table.append(record)
    return upd(db, table_name, new_table)


def del_all(db, table_name):
    table = []
    return upd(db, table_name, table)


# value level
def ret_val(db, table_name, record_id_key, record_id_value, data_key):
    # assumes [record_id_key, record_id_value] identifies a single record
    records = ret_recs(db, table_name, [[record_id_key, record_id_value]])
    if len(records) == 0:
        return None
    else:
        return ret(records[0], data_key)


def ret_val_idx(db, table_name, record_idx, data_key):
    record = ret_rec_idx(db, table_name, record_idx)
    if record:
        return ret(record, data_key)
    else:
        return None


def upd_val(db, table_name, record_id_key, record_id_val, data_key, data_val):
    # updates all records identified by [record_id_key, record_id_value]
    return upd_recs(db,
                    table_name,
                    [[record_id_key, record_id_val]],
                    [[data_key, data_val]])


# summary
def rec_cnt(db, table_name, kv_list):
    records = ret_recs(db, table_name, kv_list)
    return len(records)


def rec_list(db, table_name, key):
    list = []
    table = ret_tab(db, table_name)
    for record in table:
        for item in record:
            if item[0].lower() == key.lower():
                if not item[1] in list:
                    list.append(item[1])
    return list

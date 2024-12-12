def contact_patch(db_parser):
    # First, check if 'wxsystem' username already exists
    check_sql = '''
    SELECT COUNT(*) FROM contact WHERE UserName = 'wxsystem'
    '''
    result = db_parser.execute_sql(sql=check_sql)
    
    if result[0][0] == 0:  # If 'wxsystem' doesn't exist
        # Perform the insert
        insert_sql = '''
        INSERT INTO contact (
        Remark,
        NickName,
        UserName,
        Alias
        )
        VALUES (
            '微信系统',  -- Remark
            '微信系统',  -- NickName
            'wxsystem', -- UserName
            'wxsystem'  -- Alias
        );
        '''
        db_parser.execute_sql(sql=insert_sql)
        print("Inserted 'wxsystem' contact into the contact table.")
    else:
        print("'wxsystem' contact already exists in the contact table. No insertion performed.")

def retrieve_op_wxid(db_parser, op_id):
    sql = f"""
        Select talker
        FROM WL_MSG
        Where MsgSvrID = {op_id}
    """
    return db_parser.execute_sql(sql=sql)

def update_wechat_system_talker(db_parser):
    sql = """
    UPDATE wl_msg
    SET talker = 'wxsystem'
    WHERE talker = '微信系统'; 
    """
    db_parser.execute_sql(sql=sql)

def update_self_talker(db_parser, wxid):
    sql = f"""
    UPDATE wl_msg
    SET talker = '{wxid}'
    WHERE talker = '我';
    """
    db_parser.execute_sql(sql=sql)

# replace 我 with

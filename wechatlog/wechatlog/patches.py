def contact_patch(db_parser):
    sql = '''
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
    db_parser.execute_sql(sql=sql)

def retrieve_op_wxid(db_parser, op_id):
    sql = f"""
        Select talker
        FROM WL_MSG
        Where MsgSvrID = {op_id}
    """
    return db_parser.execute_sql(sql=sql)
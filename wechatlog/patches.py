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
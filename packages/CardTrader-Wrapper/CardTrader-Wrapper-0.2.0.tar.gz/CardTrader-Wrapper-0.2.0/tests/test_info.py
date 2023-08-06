from cardtrader.service import CardTrader


def test_info(session: CardTrader):
    result = session.info()
    assert result.info_id == 4263
    assert result.name == "BuriedInCode App 20220418050011"

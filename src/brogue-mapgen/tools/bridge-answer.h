/* Test-only helpers: answer the pending Brogue interaction of a turn result. */
static BrogueBridgeResult answerPending(BrogueBridgeTurnResult *turn, int yes) {
    BrogueBridgeInteractionResponse response;
    memset(&response, 0, sizeof(response));
    response.apiVersion = BROGUE_BRIDGE_API_VERSION;
    response.token = turn->interaction.token;
    response.answer = yes ? BROGUE_ANSWER_YES : BROGUE_ANSWER_NO;
    return brogue_bridge_respond(&response, turn);
}

static BrogueBridgeResult answerChoice(BrogueBridgeTurnResult *turn, uint64_t itemId) {
    BrogueBridgeInteractionResponse response;
    memset(&response, 0, sizeof(response));
    response.apiVersion = BROGUE_BRIDGE_API_VERSION;
    response.token = turn->interaction.token;
    response.answer = BROGUE_ANSWER_ITEM;
    response.itemId = itemId;
    return brogue_bridge_respond(&response, turn);
}

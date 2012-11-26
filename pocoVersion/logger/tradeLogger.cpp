#include "tradeLogger.h"
#include "config.h"

namespace quantrade {

TradeLogger::TradeLogger() {

}

TradeLogger::~TradeLogger() {

}

void TradeLogger::init(const std::string &logLevel, const std::string &name) {
    // console channel:
    Poco::AutoPtr<Poco::ConsoleChannel> pChannel(new Poco::ConsoleChannel);

    // formatter:
    Poco::AutoPtr<Poco::PatternFormatter> pFrmt(new Poco::PatternFormatter);
    pFrmt->setProperty("pattern", "%S.%i [%p] %s : %t");

    // formatting channel:
    Poco::AutoPtr<Poco::FormattingChannel> pFrmtC(new Poco::FormattingChannel(pFrmt, pChannel));

    Poco::Logger::root().setChannel(pFrmtC);

    Poco::Logger &log = Poco::Logger::get(name);
    log.setLevel(DEFAULT_LOG_LEVEL);
    log.debug("Logger initialized.");
}

/**
 * @details descending levels: fatal, critical, error, warning, notice, information, debug, trace
 */
void TradeLogger::setLevel(const std::string &lvl, const std::string &name) {
    Poco::Logger &log = Poco::Logger::get(name);
    log.setLevel(lvl);
}

Poco::Logger &TradeLogger::get(const std::string &name) {
    if (Poco::Logger::has(name) == NULL) {
        TradeLogger::init(DEFAULT_LOG_LEVEL, name);
    }

    return (Poco::Logger::get(name));
}

} // quantrade namespace

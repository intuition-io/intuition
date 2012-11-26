#ifndef TRADE_LOGGER_H
#define TRADE_LOGGER_H

#include <Poco/Logger.h>
#include <Poco/AutoPtr.h>
#include <Poco/PatternFormatter.h>
#include <Poco/FormattingChannel.h>
#include <Poco/ConsoleChannel.h>

#include <string>

namespace quantrade {

class TradeLogger {
    public:
        TradeLogger();
        virtual ~TradeLogger();

        static void init(const std::string &logLevel, const std::string &name);
        static void setLevel(const std::string &lvl, const std::string &name);

        static Poco::Logger &get(const std::string &name);
};

} // quantrade namespace

#endif /* TRADE_LOGGER_H */

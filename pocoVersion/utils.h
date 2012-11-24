#include <boost/lexical_cast.hpp>
#define toStr(msg) boost::lexical_cast<string>(msg)

#define TRACE "(" + toStr(__FILE__) + ":" +toStr(__LINE__) + ")"

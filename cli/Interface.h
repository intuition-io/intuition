#ifndef DEF_INTERFACE
#define DEF_INTERFACE

#include <string>
#include <vector>
#include <fstream>
#include <sstream>

class Interface {
    // Methods
    public:
    Interface();
    Interface(std::string index_f, std::string conf_f, std::string days, std::string precision, std::string rss);
    ~Interface();
    void cmd_parser(std::string cmd_line);
    int config_file_generator();
    std::string accessDb();

    // Attributes
    private:
    std::vector<std::string> cmd_m;
    std::vector<std::string> stocks_list_m;
    std::string const index_f_m;
    std::string const conf_f_m;
    std::string stock_m[6];
    std::string parameters_m[3];
    // Penser aux maps, plus intuitifs
};

#endif

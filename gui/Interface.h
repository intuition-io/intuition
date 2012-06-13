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
    ~Interface();
    void cmd_parser(std::string cmd_line_edit);
    void config_file_generator();
    QString infos_printer();

    // Attributes
    private:
    std::vector<std::string> cmd_m;
    std::vector<std::string> stocks_list_m;
    std::string const index_f_m;
    std::string const conf_f_m;
    std::string stock_m[6];
};

#endif

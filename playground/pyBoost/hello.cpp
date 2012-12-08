#include <iostream>
#include <boost/python.hpp>
#include <Python.h>

namespace py = boost::python;

int main(){
    // Must be called before any boost::python functions
    Py_Initialize();
    // import the main module
    py::object main_module = py::import("__main__");
    // load the dictionary object out of the main module
    py::object main_namespace = main_module.attr("__dict__");
    // run simple code within the main namespace using the boost::python::exec 
    //  function
    py::exec("print 'Hello, world'", main_namespace);
    // any valid Python will execute
    py::exec("print 'Hello, world'[3:5]", main_namespace);
    // it is as if you opened a new Python file and wrote the commands
    // all of the normal functionality is available
    py::exec("print '.'.join(['1','2','3'])", main_namespace);

    // of course, you can also import functionality from the standard library
    py::exec("import random", main_namespace);
    // boost::python::eval will return the result of an expression 
    //  as a boost::python::object
    py::object rand = py::eval("random.random()", main_namespace);
    // the boost::python::extract function can then convert to C++ data types
    //  (only as appropriate, of course)
    std::cout << py::extract<double>(rand) << std::endl;

    // or, if you'd prefer, you can extract the functions themselves into objects
    //  then call them as you wish from C++. this is akin to what we did at the top
    //  of this file. you can't execute code with the exec function, though, without
    //  extracting the namespace object as we did with __main__ above.
    // this method ultimately provides a much cleaner way of interacting with Python
    //  objects over their lifetimes

    // import the random module
    py::object rand_mod = py::import("random");
    // extract the random function from the random module (random.random())
    py::object rand_func = rand_mod.attr("random");
    // call the function and extract the result
    //  [sidenote: this sort of syntax is what makes boost::python so valuable]
    py::object rand2 = rand_func();
    std::cout << py::extract<double>(rand2) << std::endl;
}

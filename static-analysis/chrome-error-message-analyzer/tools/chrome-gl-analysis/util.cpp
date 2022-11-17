#include <string>
#include <algorithm>

#include "util.h"

std::string
trim( std::string const& original )
{
    std::string::const_iterator right = std::find_if( original.rbegin(), original.rend(), IsNotSpace() ).base();
    std::string::const_iterator left = std::find_if(original.begin(), right, IsNotSpace() );
    return std::string( left, right );
}

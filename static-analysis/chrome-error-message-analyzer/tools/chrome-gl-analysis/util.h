#ifndef UTIL_H_
#define UTIL_H_

#include <locale>
#include <algorithm>

// copied from
// https://stackoverflow.com/questions/9358718/similar-function-in-c-to-pythons-strip
//

template <std::ctype_base::mask mask>
class IsNot
{
    std::locale myLocale;       // To ensure lifetime of facet...
    std::ctype<char> const* myCType;
public:
    IsNot( std::locale const& l = std::locale() )
        : myLocale( l )
        , myCType( &std::use_facet<std::ctype<char> >( l ) )
    {
    }
    bool operator()( char ch ) const
    {
        return ! myCType->is( mask, ch );
    }
};

typedef IsNot<std::ctype_base::space> IsNotSpace;

std::string
trim(std::string const& original);

#endif // UTIL_H_

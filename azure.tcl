# Файл с темой Azure для tkinter
namespace eval ttk::theme::azure {
    variable colors
    array set colors {
        -fg             "#ffffff"
        -bg             "#333333"
        -disabledfg     "#aaaaaa"
        -disabledbg     "#444444"
        -selectfg       "#ffffff"
        -selectbg       "#007fff"
    }

    ttk::style theme create azure -parent clam -settings {
        ttk::style configure . \
            -background $colors(-bg) \
            -foreground $colors(-fg) \
            -troughcolor $colors(-bg) \
            -focuscolor $colors(-selectbg) \
            -selectbackground $colors(-selectbg) \
            -selectforeground $colors(-selectfg) \
            -fieldbackground $colors(-bg) \
            -font TkDefaultFont \
            -borderwidth 1 \
            -relief flat

        ttk::style map . -foreground [list disabled $colors(-disabledfg)]

        ttk::style configure TButton -padding {10 5} -anchor center
        ttk::style map TButton \
            -background [list hover "#555555"] \
            -relief [list pressed sunken]

        ttk::style configure TLabelframe -background $colors(-bg)
        ttk::style configure TLabelframe.Label -foreground $colors(-fg)

        ttk::style configure TNotebook -background $colors(-bg)
        ttk::style configure TNotebook.Tab \
            -padding {10 5} \
            -background $colors(-bg) \
            -foreground $colors(-fg)
        ttk::style map TNotebook.Tab \
            -background [list selected "#555555"] \
            -foreground [list selected "#ffffff"]

        ttk::style configure TEntry -fieldbackground white
        ttk::style configure TProgressbar -background "#007fff"
    }
}

package provide ttk::theme::azure 1.0
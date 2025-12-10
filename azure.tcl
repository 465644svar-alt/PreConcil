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
        -warning        "#ff9900"
        -success        "#00cc00"
        -error          "#ff3333"
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

        ttk::style configure Accent.TButton \
            -padding {15 7} \
            -font {TkDefaultFont 10 bold}
        ttk::style map Accent.TButton \
            -background [list hover "#0055cc"] \
            -relief [list pressed sunken]

        ttk::style configure Warning.TButton \
            -background $colors(-warning) \
            -foreground black
        ttk::style map Warning.TButton \
            -background [list hover "#ffaa00"] \
            -relief [list pressed sunken]

        ttk::style configure Error.TButton \
            -background $colors(-error) \
            -foreground white
        ttk::style map Error.TButton \
            -background [list hover "#ff5555"] \
            -relief [list pressed sunken]

        ttk::style configure Success.TButton \
            -background $colors(-success) \
            -foreground white
        ttk::style map Success.TButton \
            -background [list hover "#00ee00"] \
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

        ttk::style configure StatusIndicator.TFrame \
            -background $colors(-bg) \
            -relief groove \
            -borderwidth 2

        ttk::style configure StatusText.TLabel \
            -font {TkDefaultFont 10} \
            -padding {5 2}

        ttk::style configure StatusGood.TLabel \
            -foreground $colors(-success) \
            -font {TkDefaultFont 10 bold}

        ttk::style configure StatusWarning.TLabel \
            -foreground $colors(-warning) \
            -font {TkDefaultFont 10 bold}

        ttk::style configure StatusError.TLabel \
            -foreground $colors(-error) \
            -font {TkDefaultFont 10 bold}
    }
}

package provide ttk::theme::azure 1.0
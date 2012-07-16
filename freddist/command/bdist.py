from distutils.command.bdist import bdist as _bdist


def show_formats():
    """Print list of available formats (arguments to "--format" option).
    """
    from distutils.fancy_getopt import FancyGetopt
    formats = []
    for fmt in bdist.format_commands:
        formats.append(("formats=" + fmt, None,
                        bdist.format_command[fmt][1]))
    pretty_printer = FancyGetopt(formats)
    pretty_printer.print_help("List of available distribution formats:")


class bdist(_bdist):
    user_options = _bdist.user_options
    boolean_options = _bdist.boolean_options
    format_commands = _bdist.format_commands + ['deb']
    format_command = _bdist.format_command
    format_command.update({'deb': ('bdist_deb',  "Debian distribution")})

    help_options = [
        ('help-formats', None,
         "lists available distribution formats", show_formats),
        ]

    user_options.append(('build-extra-opts=', None,
        'extra option(s) passed to build command'))
    user_options.append(('install-extra-opts=', None,
        'extra option(s) passed to install command'))
    user_options.append(('dontpreservepath', None,
        'do not automatically append `--preservepath\'\
        option to `install-extra-opts\''))

    boolean_options.append('dontpreservepath')

    def initialize_options(self):
        self.build_extra_opts   = None
        self.install_extra_opts = None
        self.dontpreservepath   = None

        _bdist.initialize_options(self)

    def finalize_options(self):
        if not self.build_extra_opts:
            self.build_extra_opts = ''
        
        if not self.install_extra_opts and not self.dontpreservepath:
            self.install_extra_opts = '--preservepath'
        elif self.install_extra_opts and not self.dontpreservepath:
            if self.install_extra_opts.find('--preservepath') == -1:
                self.install_extra_opts = \
                        self.install_extra_opts + ' --preservepath'
        elif self.install_extra_opts and self.dontpreservepath:
            pass
        else:
            self.install_extra_opts = ''

        _bdist.finalize_options(self)

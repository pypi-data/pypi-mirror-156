Utilities and command line for working with EBooks.
Basic support for talking to Apple Books, Calibre, Kindle, Mobi.

*Latest release 20220626*:
* CalibreBook: new setter mode for .tags, CalibreCommand: new cmd_tags to update tags.
* CalibreBook.pull_format: AZW formats: also check for AZW4.
* CalibreCommand.books_from_spec: /regexp: search the tags as well.
* CalibreBook: subclass FormatableMixin; CalibreCommand.cmd_ls: new "-o ls_format" option for the top line format.

These form the basis of my personal Kindle and Calibre workflow.

# Release Log



*Release 20220626*:
* CalibreBook: new setter mode for .tags, CalibreCommand: new cmd_tags to update tags.
* CalibreBook.pull_format: AZW formats: also check for AZW4.
* CalibreCommand.books_from_spec: /regexp: search the tags as well.
* CalibreBook: subclass FormatableMixin; CalibreCommand.cmd_ls: new "-o ls_format" option for the top line format.

*Release 20220606*:
Initial PyPI release.

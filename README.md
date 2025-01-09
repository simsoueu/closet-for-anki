# Closet Note Type Reloaded

This Anki add-on enhances the functionality of the Closet note type by providing additional features and customization options. It allows users to manage and update their Closet notes more efficiently.

This extension is my take on the [Anki Closet](https://ankiweb.net/shared/info/272311064), I'm not claiming to have created the Closet for Anki, I only took some parts and create an extension to automate the process of enabling `cmds` fields.

## Features

- **Highlight Cloze Tags**: Customize the color of cloze tags in your notes.
- **Show/Hide Deck Name**: Toggle the visibility of the deck name as a header.
- **Automatic Field Management**: Automatically manage and update `cmds` fields based on the content of your notes.
- **Menu Integration**: Adds a "Closet" menu to Anki's Tools menu for easy access to settings and updates.
- **Works both on Web and Ankdroid**: As long as you created valid notes.

# Description

From the original Closet For Anki:

> Closet is a unique mix between a templating engine and a markup language written in TypeScript for the generation of flashcards, especially for the use in the Anki flashcard software.

# Requirements

Only tested with Anki for Desktop version 24.11 (Qt version 6)

## Installation

1. Download the add-on and place it in your Anki add-ons folder.
2. Restart Anki to load the add-on.

## Usage

### Configuration

1. Open Anki and go to the "Tools" menu.
2. Select "Closet" and then "Settings".
3. In the settings dialog, you can:
   - Choose a color for the cloze tags.
   - Enable or disable highlighting for all cloze tags.
   - Show or hide the deck name as a header.

### Updating Notes

1. Open Anki and go to the "Tools" menu.
2. Select "Closet" and then "Update Closet Cards".
3. This will update all Closet notes based on the current settings.

## Development

### Project Structure

The project is organized into the following modules:

- `__init__.py`: Initializes the add-on and sets up hooks.
- `config.py`: Manages loading and saving configuration settings.
- `hooks.py`: Sets up the necessary hooks for the add-on.
- `menu.py`: Manages the Closet menu and settings dialog.
- `closet_note_updater.py`: Handles updating and managing Closet notes.

## Contributing

Contributions are welcome! If you have any ideas for new features or improvements, feel free to open an issue or submit a pull request.

## License

This project is licensed under the GPLv3 License. See the [LICENSE](https://www.gnu.org/licenses/gpl-3.0.txt) file for details.

## Acknowledgements

Special thanks to the Anki community for their support and contributions to this project.

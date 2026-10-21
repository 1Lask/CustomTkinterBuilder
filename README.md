# CustomTkinter Builder — Free Layout Switch

CustomTkinter Builder is a free and open-source visual UI builder for [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter). It helps you create interfaces visually and export them as Python code.

This branch, `feature/free-layout-switch`, builds on the original project by adding a switchable free-positioning workflow while retaining the original `pack()` layout workflow.

> **Project status:** This is a community-maintained modification on a feature branch of the original project. It is not an official release from the original author. Please check the repository's [Releases](https://github.com/1Lask/CustomTkinterBuilder/releases) for available builds.

## What's new in this branch

### Switch between layout modes

- **Pack mode (`pack()`)** — keeps the original layout workflow, including its packing options.
- **Free layout mode (`place()`)** — position widgets using explicit X/Y coordinates.
- Switch between modes from the application without losing the saved free-layout coordinates.
- Existing projects that do not contain layout-mode information default to Pack mode for compatibility.

### Move and resize widgets

- Drag widgets to reposition them while using free layout mode.
- Resize widgets using the visual resize handle.
- Edit X, Y, width, and height in the properties panel while in free layout mode.
- Edit the original Pack options, such as side, fill, expand, and padding, while in Pack mode.

### Save and export

- Save project layout information in the project's JSON file, including the selected layout mode and free-positioning geometry.
- Export Python code in both standard and object-oriented (OOP) formats.
- Generated code supports the selected layout manager, including `place()` geometry for free-layout projects.

### Additional fixes

- Apply widget padding changes without unnecessarily removing and reinserting the widget, helping preserve widget order and selection.
- Update the main preview window title from the properties panel.
- Handle CustomTkinter widget dimensions correctly when applying `place()` geometry.

These changes are part of the feature branch and may not be present in the original project's published release.

## Features from the original project

- Visual, drag-and-drop interface building.
- Configure widget properties.
- Support for the original `pack()` layout workflow and the added `place()` free-layout workflow.
- Built-in widget presets and icon support.
- Palette tools for changing UI colors.
- Vertical and horizontal scrollable frames.
- Export Python code in standard or OOP format.
- Save and reopen projects as JSON.
- Duplicate and delete widgets, change their order, and change their parent.
- Inspect the interface hierarchy using the hierarchy panel.
- Work with light and dark appearance modes.
- Add images and customize fonts.

## Available widgets

The original project includes these widget types:

- Frame
- Button
- Label
- Entry
- Vertical Scrollable Frame
- Horizontal Scrollable Frame
- Switch
- Check Box
- Radio Button
- Segmented Button
- Horizontal Slider
- Vertical Slider
- Combo Box
- Option Menu
- Text Box
- Progress Bar
- Vertical Scrollbar
- Horizontal Scrollbar

## Screenshots and examples

The images below are from the original project's README and demonstrate its existing UI-building capabilities.

### Login

**Dark mode**

![Dark Mode - Login](https://github.com/rigvedmaanas/CustomTkinterBuilder/assets/77579661/133ef73f-3b55-4181-bf78-a4ba1e9b19a3)

**Light mode**

![Light Mode - Login](https://github.com/rigvedmaanas/CustomTkinterBuilder/assets/77579661/482ed8c3-0573-4103-9aa6-45d0258eacdf)

### Music player

**Dark mode**

![Dark Mode - Spotify](https://github.com/rigvedmaanas/CustomTkinterBuilder/assets/77579661/28970507-3125-4cd8-bb42-d6a7d3fee359)

**Light mode**

![Light Mode - Spotify](https://github.com/rigvedmaanas/CustomTkinterBuilder/assets/77579661/eb2a3b08-02ac-4bea-bf5f-9da723bb6101)

### Video library

![Video library](https://github.com/rigvedmaanas/CustomTkinterBuilder/assets/77579661/612572d7-456c-45ef-aeff-ea1108cbf995)

## Download

Check the [GitHub Releases page](https://github.com/1Lask/CustomTkinterBuilder/releases) for available downloads. A Windows executable can be attached to a release when a build is published.

## Run from source

Python and the dependencies listed in `requirements.txt` are required.

```powershell
git clone https://github.com/1Lask/CustomTkinterBuilder.git
cd CustomTkinterBuilder
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe main.py
```

To try the free-layout changes, check out the `feature/free-layout-switch` branch:

```powershell
git switch feature/free-layout-switch
```

## Documentation

The original project's [Wiki](https://github.com/rigvedmaanas/CustomTkinterBuilder/wiki) may still be useful for features that have not changed.

## Credits and acknowledgements

- **Original project:** [CustomTkinter Builder by Rigved Maana](https://github.com/rigvedmaanas/CustomTkinterBuilder). The original project, its existing features, and its assets remain credited to their respective creators.
- **Feature-branch maintainer:** [1Lask](https://github.com/1Lask), for maintaining this repository branch and integrating the changes.
- **AI development assistance:** ChatGPT by OpenAI assisted with implementation planning, code changes, debugging, and documentation for the free-layout feature and related fixes. ChatGPT is an AI assistant, not a human contributor or copyright holder.

This acknowledgement does not imply that OpenAI or the original author officially endorses this branch.

## License

Please refer to the repository's [LICENSE](LICENSE) file for the applicable license. The original README states that projects and code generated with CustomTkinter Builder belong to the user; consult the license and original project terms for details.

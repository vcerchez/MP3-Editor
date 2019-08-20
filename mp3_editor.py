# MP3 Editor v.2 (20/08/2019)

import wx
import subprocess as sp
import os
import os.path
import sys
import re

version = 'Aug 20, 2019'

class MainFrame(wx.Frame):
    ''' Main window'''
    
    def __init__(self):
        # Initialize main window, 
        # disable window resizing with proper style
        super().__init__(parent=None, 
                         title='MP3 Editor ' + f'(version {version})', 
                         size=(900,400), 
                         style=wx.DEFAULT_FRAME_STYLE & \
                             ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX))
        
        # Status bar
        self.statusbar = self.CreateStatusBar()
        
        # Initialize Main Panel
        self.main_panel = MainPanel(self)
        # Create menu
        self.create_menu()
        # Draw Main window
        self.Show()
        
    # Menu
    def create_menu(self):
        # Initialize Menu bar
        menu_bar = wx.MenuBar()
        
        # Initialize Menu
        file_menu = wx.Menu()
        
        # Append entries to File menu
        open_menu_item = file_menu.Append(wx.ID_OPEN, 
                                          '&Open', 
                                          'Open a multimedia file')
        save_menu_item = file_menu.Append(wx.ID_SAVE, 
                                          '&Process and Save', 
                                          'Extract audio track, ' +\
                                          'process and save it')
        file_menu.AppendSeparator()
        exit_menu_item = file_menu.Append(wx.ID_EXIT, 
                                          'E&xit', 
                                          'Exit the program')
        
        # Append Menu to Bar with name File
        menu_bar.Append(file_menu, '&File')
        
        # Bind events
        self.Bind(event=wx.EVT_MENU, 
                  handler=self.on_open, 
                  source=open_menu_item)
        self.Bind(event=wx.EVT_MENU, 
                  handler=self.on_save, 
                  source=save_menu_item)
        self.Bind(event=wx.EVT_MENU, 
                  handler=self.on_exit, 
                  source=exit_menu_item)
        
        # Draw Menu bar
        self.SetMenuBar(menu_bar)
        
    def on_open(self, event):
        '''Event handler for Open menu'''
        # Initialize Open file dialog box
        wildcard = 'MP3 or MP4 file (*.mp3;*.mp4)|*.mp3;*.mp4'
        dlg = wx.FileDialog(self, 
                            message='Choose an MP3 file', 
                            defaultDir='', 
                            defaultFile='', 
                            wildcard=wildcard, 
                            style=wx.FD_OPEN | wx.FD_MULTIPLE)
        
        # Show Open file dialog box and wait for action
        # Process selected files
        if dlg.ShowModal() == wx.ID_OK:
            # Get the paths to the selected files    
            # Apdate file list
            paths = dlg.GetPaths()
            
            for path in paths:
                
                folder = os.path.dirname(path)
                file_name = os.path.basename(path)

                # Extract metadata
                (bitrate, 
                 artist, 
                 album, 
                 title, 
                 track_num) = parse_metadata(path)

                # Append to list of files
                self.main_panel.files.append(Track(path, 
                                                   folder, 
                                                   file_name, 
                                                   bitrate, 
                                                   artist, 
                                                   album, 
                                                   title, 
                                                   track_num))
            
            self.main_panel.update_list()
        
        # Close Open file dialog box
        dlg.Destroy()
    
    def on_save(self, event):
        '''Event handler for Save menu'''            
        # If no file selected - break
        if self.main_panel.list_ctrl.GetSelectedItemCount() < 1:
            return
        
        # Initialize Folder selection dialog box
        dlg = wx.DirDialog(self, 
                            message='Save processed MP3 file to folder:', 
                            defaultPath='', 
                            name='name')
        
        # Show Folder dialog and wait for action
        # Get path
        if dlg.ShowModal() == wx.ID_OK:
            save_path = dlg.GetPath()
        
        dlg.Destroy()
        
        selected = -1
        
        # List of functions to check the status (finished or not yet) 
        # of ffmpeg processes launched
        process_poll = []
        
        # Process and save selected files
        while True:
            selected = \
            self.main_panel.list_ctrl.GetNextItem(selected, 
                                                    wx.LIST_NEXT_ALL, 
                                                    wx.LIST_STATE_SELECTED)
            
            # Break when reach the end of selected files
            if selected == -1:
                break
            
            input_file = self.main_panel.files[selected].path
            file_name, _ = os.path.splitext(
                            self.main_panel.files[selected].file_name)
            output_file = os.path.join(save_path, file_name + '.mp3')
            
            volume_level = self.main_panel.files[selected].volume
            
            bitrate = int(self.main_panel.files[selected].bitrate)
            bitrate_option = bitrate_to_option(bitrate)
            
            artist = self.main_panel.files[selected].artist
            album = self.main_panel.files[selected].album
            title = self.main_panel.files[selected].title
            track_num = self.main_panel.files[selected].track_num
            
            # ffmpeg command
            # Double quotes around file paths are needed to handle 
            # white spaces in path
            cmd = f'ffmpeg -y -i "{input_file}" ' +\
                  f'-filter:a "volume={volume_level}" ' +\
                  f'-codec:a libmp3lame ' +\
                  f'-qscale:a {bitrate_option} ' +\
                  f'-metadata artist="{artist}" ' +\
                  f'-metadata album="{album}" ' +\
                  f'-metadata title="{title}" ' +\
                  f'-metadata track="{track_num}" ' +\
                  f'"{output_file}"'
            
            # run the ffmpeg command
            ffmpeg_process = sp.Popen(cmd, **subprocess_args(False, False, False))
            process_poll.append(ffmpeg_process.poll)
        
        # Check status of ffmpeg processes
        status = [poll_func() for poll_func in process_poll]
        while None in status:
            self.statusbar.SetStatusText('Working...')
            status = [poll_func() for poll_func in process_poll]
        
        # Set status 'Done'
        self.statusbar.SetStatusText('Done')
    
    def on_exit(self, event):
        '''Event handler for Exit menu'''
        self.Destroy()

class MainPanel(wx.Panel):
    '''Create main panel'''
    def __init__(self, parent):
        # Initialize panel
        super().__init__(parent)
        
        # Initialize file list
        self.files = []
        
        # Sizers
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        # Initialize table to list opened files
        self.list_ctrl = wx.ListCtrl(self, 
                                     size=(-1, -1), 
                                     style=wx.LC_REPORT | wx.BORDER_SUNKEN)
        
        # Create columns
        self.list_ctrl.InsertColumn(0, '', width=30)
        self.list_ctrl.InsertColumn(1, 'File', width=200)
        self.list_ctrl.InsertColumn(2, 'Volume', width=60)
        self.list_ctrl.InsertColumn(3, 'Bitrate', width=60)
        self.list_ctrl.InsertColumn(4, 'Artist', width=100)
        self.list_ctrl.InsertColumn(5, 'Album', width=100)
        self.list_ctrl.InsertColumn(6, 'Title', width=255)
        self.list_ctrl.InsertColumn(7, 'Track', width=45)
        
        # Add table to main sizer
        main_sizer.Add(self.list_ctrl, 1, wx.ALL | wx.EXPAND, 5)
        
        # Buttons
        selectall_button = wx.Button(self, label='Select all')
        selectall_button.Bind(wx.EVT_BUTTON, self.on_select_all)
        button_sizer.Add(selectall_button, 1, wx.EXPAND)
        
        remove_button = wx.Button(self, label='Remove')
        remove_button.Bind(wx.EVT_BUTTON, self.on_remove)
        button_sizer.Add(remove_button, 1, wx.EXPAND)
        
        volume_button = wx.Button(self, label='Volume')
        volume_button.Bind(wx.EVT_BUTTON, self.on_volume)
        button_sizer.Add(volume_button, 1, wx.EXPAND)
        
        bitrate_button = wx.Button(self, label='Bitrate')
        bitrate_button.Bind(wx.EVT_BUTTON, self.on_bitrate)
        button_sizer.Add(bitrate_button, 1, wx.EXPAND)
        
        artist_button = wx.Button(self, label='Artist')
        artist_button.Bind(wx.EVT_BUTTON, self.on_artist)
        button_sizer.Add(artist_button, 1, wx.EXPAND)
        
        album_button = wx.Button(self, label='Album')
        album_button.Bind(wx.EVT_BUTTON, self.on_album)
        button_sizer.Add(album_button, 1, wx.EXPAND)
        
        title_button = wx.Button(self, label='Title')
        title_button.Bind(wx.EVT_BUTTON, self.on_title)
        button_sizer.Add(title_button, 1, wx.EXPAND)
        
        track_num_button = wx.Button(self, label='Track')
        track_num_button.Bind(wx.EVT_BUTTON, self.on_track_num)
        button_sizer.Add(track_num_button, 1, wx.EXPAND)
        
        # Add button sizer to main sizer
        main_sizer.Add(button_sizer, 0, wx.ALL | wx.EXPAND, 5)
        
        # Run main sizer
        self.SetSizer(main_sizer)
        
    def on_select_all(self, event):
        num_items = self.list_ctrl.GetItemCount()
        for i in range(num_items):
            self.list_ctrl.Select(i)
    
    def on_remove(self, event):
        '''Remove file from the list'''
        selected = -1
        to_drop = []
        
        # Get indices of selected files
        while True:
            selected = self.list_ctrl.GetNextItem(selected, 
                                                  wx.LIST_NEXT_ALL, 
                                                  wx.LIST_STATE_SELECTED)
            
            if selected == -1:
                break
            
            to_drop.append(selected)
        
        # Remove these files from the list starting from the last one
        for i in sorted(to_drop, reverse=True):
            del self.files[i]
            
        # Re-draw the table
        self.update_list()
            
    def on_volume(self, event):
        '''Set volume multiplier coeff'''
        # If nothing selected
        if self.list_ctrl.GetFirstSelected() == -1:
            return
        
        # Ask user to enter volume level
        volume_x = wx.GetNumberFromUser('Multiply' +\
                                        'current auduio volume level by', 
                                        '\u00D7', 
                                        'Volume', 1, 0, 100)
        
        # If user cancel - break
        if volume_x == -1:
            return
        
        selected = -1
        
        # Update volume values
        while True:
            selected = self.list_ctrl.GetNextItem(selected, 
                                                  wx.LIST_NEXT_ALL, 
                                                  wx.LIST_STATE_SELECTED)
            
            if selected == -1:
                break
            
            self.files[selected].volume = volume_x
        
        # Re-draw the table
        self.update_list()
        
    def on_bitrate(self, event):
        '''Set new bitrate'''
        # If nothing selected
        if self.list_ctrl.GetFirstSelected() == -1:
            return
        
        # Ask user to enter bitrate
        new_bitrate = wx.GetNumberFromUser('Set new bitrate', 
                                           '\u2248', 
                                           'Bitrate', 130, 65, 245)
        # If user cancel - break
        if new_bitrate == -1:
            return
        
        selected = -1
        
        # Update bitrate values
        while True:
            selected = self.list_ctrl.GetNextItem(selected, 
                                                  wx.LIST_NEXT_ALL, 
                                                  wx.LIST_STATE_SELECTED)
            
            if selected == -1:
                break
            
            self.files[selected].bitrate = new_bitrate
        
        # Re-draw the table
        self.update_list()
    
    def on_artist(self, event):
        '''Edit Artist'''
        # If nothing selected
        if self.list_ctrl.GetFirstSelected() == -1:
            return
        
        # Ask user to enter artist name 
        current_name = self.files[self.list_ctrl.GetFirstSelected()].artist
        dlg = wx.TextEntryDialog(self, 
                                 message="Enter artist's name", 
                                 caption='Artist', 
                                 value=current_name)
            
        if dlg.ShowModal() == wx.ID_OK:
            artist = dlg.GetValue()
            
            selected = -1
            
            # Update artist name
            while True:
                selected = \
                self.list_ctrl.GetNextItem(selected, 
                                           wx.LIST_NEXT_ALL, 
                                           wx.LIST_STATE_SELECTED)
            
                if selected == -1:
                    break
            
                self.files[selected].artist = artist
            
            # Re-draw table
            self.update_list()

        dlg.Destroy()
        
    def on_album(self, event):
        '''Edit Album'''
        # If nothing selected
        if self.list_ctrl.GetFirstSelected() == -1:
            return
        
        # Ask user to enter album name 
        current_name = self.files[self.list_ctrl.GetFirstSelected()].album
        dlg = wx.TextEntryDialog(self, 
                                 message="Enter album's name", 
                                 caption='Album', 
                                 value=current_name)
            
        if dlg.ShowModal() == wx.ID_OK:
            album = dlg.GetValue()
            
            selected = -1
            
            # Update album name
            while True:
                selected = \
                self.list_ctrl.GetNextItem(selected, 
                                           wx.LIST_NEXT_ALL, 
                                           wx.LIST_STATE_SELECTED)
            
                if selected == -1:
                    break
            
                self.files[selected].album = album
            
            # Re-draw table
            self.update_list()

        dlg.Destroy()
    
    def on_title(self, event):
        '''Edit title'''
        selected = self.list_ctrl.GetFirstSelected()
        
        # If no file selected or many items selected - break
        if self.list_ctrl.GetSelectedItemCount() == 0:
            return
        
        # If one selected
        elif self.list_ctrl.GetSelectedItemCount() == 1:
            # Ask user to enter a title
            dlg = wx.TextEntryDialog(self, 
                                     message="Enter a title", 
                                     caption='Title', 
                                     value=self.files[selected].title)

            # Get the title and update file list
            if dlg.ShowModal() == wx.ID_OK:
                title = dlg.GetValue()
                self.files[selected].title = title

            # Re-draw table
            self.update_list()

            dlg.Destroy()
            return
        
        # TO FINISH
        # If multiple selected
        elif self.list_ctrl.GetSelectedItemCount() > 1:
            message = "Track titles will be generated automatically" +\
                        " from the names of the files. Proceed?"
            dlg = wx.MessageDialog(self, 
                                   message=message, 
                                   caption='Track numbers', 
                                   style=wx.YES|wx.NO|wx.CENTRE, 
                                   pos=wx.DefaultPosition)
            
            if dlg.ShowModal() == wx.ID_YES:
                for file in self.files:
                    file.title, _ = os.path.splitext(file.file_name)
                
                # Re-draw table
                self.update_list()
                return
    
    def on_track_num(self, event):
        '''Edit Track number'''
        selected = self.list_ctrl.GetFirstSelected()
        
        # If no file selected or many items selected - break
        if self.list_ctrl.GetSelectedItemCount() == 0:
            return
        
        # If a single file is selected
        elif self.list_ctrl.GetSelectedItemCount() == 1:
            track_num = wx.GetNumberFromUser('Enter track number:', 
                                             'n°', 
                                             'Track number', 
                                             self.files[selected].track_num, 
                                             0, 
                                             10000)
            # If user cancel - break
            if track_num == -1:
                return
            
            # Update track number
            self.files[selected].track_num = track_num
            # Re-draw table
            self.update_list()
            return
        
        # If multiple (2 and more) files are selected - generate automatically 
        # track numbers for all files in the list
        elif self.list_ctrl.GetSelectedItemCount() > 1:
            message = "Track numbers will be generated automatically" +\
                        " for all files in the list. Proceed?"
            dlg = wx.MessageDialog(self, 
                                   message=message, 
                                   caption='Track numbers', 
                                   style=wx.YES|wx.NO|wx.CENTRE, 
                                   pos=wx.DefaultPosition)
            
            if dlg.ShowModal() == wx.ID_YES:
                
                index = 1
                for file in self.files:
                    file.track_num = index
                    index += 1
                
                # Re-draw table
                self.update_list()
                return
    
    def update_list(self):
        '''Update table with file list'''
        
        self.list_ctrl.DeleteAllItems()
        index = 0
        
        for file in self.files:
            self.list_ctrl.InsertItem(index, str(index + 1))
            self.list_ctrl.SetItem(index, 1, file.file_name)
            self.list_ctrl.SetItem(index, 2, '\u00D7' + str(file.volume))
            self.list_ctrl.SetItem(index, 3, str(file.bitrate) + ' kb/s')
            self.list_ctrl.SetItem(index, 4, str(file.artist))
            self.list_ctrl.SetItem(index, 5, str(file.album))
            self.list_ctrl.SetItem(index, 6, str(file.title))
            self.list_ctrl.SetItem(index, 7, str(file.track_num))
            
            index += 1

class Track:
    '''Container for audio track info'''
    def __init__(self, 
                 path, 
                 folder, 
                 file_name, 
                 bitrate, 
                 artist, 
                 album, 
                 title, 
                 track_num):
        self.path = path
        self.folder = folder
        self.file_name = file_name
        self.volume = 1
        self.bitrate = bitrate
        
        self.artist = artist
        self.album = album
        self.title = title
        self.track_num = track_num

# The function suppresses the pop-up of the windows shell 
# when executing the precompiled exe file.
# Taken from https://github.com/pyinstaller/pyinstaller/wiki/Recipe-subprocess
# and slightly modified.
def subprocess_args(include_stdout=True, include_stdin=True, include_stderr=True):
    # The following is true only on Windows.
    if hasattr(sp, 'STARTUPINFO'):
        # On Windows, subprocess calls will pop up a command window by default
        # when run from Pyinstaller with the ``--noconsole`` option. Avoid this
        # distraction.
        si = sp.STARTUPINFO()
        si.dwFlags |= sp.STARTF_USESHOWWINDOW
        # Windows doesn't search the path by default. Pass it an environment so
        # it will.
        env = os.environ
    else:
        si = None
        env = None

    # ``subprocess.check_output`` doesn't allow specifying ``stdout``::
    #
    #   Traceback (most recent call last):
    #     File "test_subprocess.py", line 58, in <module>
    #       **subprocess_args(stdout=None))
    #     File "C:\Python27\lib\subprocess.py", line 567, in check_output
    #       raise ValueError('stdout argument not allowed, it will be overridden.')
    #   ValueError: stdout argument not allowed, it will be overridden.
    #
    # So, add it only if it's needed.
    if include_stdout:
        ret = {'stdout': sp.PIPE}
    else:
        ret = {}

    # On Windows, running this from the binary produced by Pyinstaller
    # with the ``--noconsole`` option requires redirecting everything
    # (stdin, stdout, stderr) to avoid an OSError exception
    # "[Error 6] the handle is invalid."
#     ret.update({'stdin': sp.PIPE,
#                 'stderr': sp.PIPE,
#                 'startupinfo': si,
#                 'env': env })
    if include_stdin:
        ret.update({'stdin': sp.PIPE})
    else:
        pass
    
    if include_stderr:
        ret.update({'stderr': sp.PIPE})
    else:
        pass
    
    
    ret.update({'startupinfo': si,
                'env': env })
    
    return ret

def bitrate_to_option(bitrate):
    '''
    Convert bitrate value (in kb/s) 
    to ffmpeg option (0-9 integer)
    '''
    # List of possible bitrates (average values) in ffmpeg
    kbs = [245, 225, 190, 175, 165, 130, 115, 100, 85, 65]
    
    for index, value in enumerate(kbs):
        kbs[index] = abs(value - bitrate)
    
    # Find closest bitrate
    min_diff = min(kbs)
    
    # ffmpeg bitrate option
    q = kbs.index(min_diff)
    
    return q

def parse_metadata(path):
    '''
    Parse metadata to extract: 
        bitrate (kb/s)
        artist name
        album name
        title
        track number
        '''
    # Read metadata and convert it to string
    # Double quotes are need to handle e.g. white spaces in path
    cmd = f'ffmpeg -i "{path}" -f ffmetadata'
    pipe = sp.Popen(cmd, **subprocess_args(False, True, True))
    infos = pipe.stderr.read().decode('utf-8')
    
    # Bitrate
    pattern = r'audio\s*:.*\s(\d+)\s*kb/s'
    result = re.search(pattern, infos.lower(), flags=re.DOTALL)
    bitrate = result.group(1) if result is not None else ''
    
    # Artist name
    pattern = r'(artist|Artist|ARTIST)\s*:\s*([^\n\r]+)'
    result = re.search(pattern, infos)
    artist = result.group(2) if result is not None else ''
    
    # Album
    pattern = r'(album|Album|ALBUM)\s*:\s*([^\n\r]+)'
    result = re.search(pattern, infos)
    album = result.group(2) if result is not None else ''
    
    # Title
    pattern = r'(title|Title|TITLE)\s*:\s*([^\n\r]+)'
    result = re.search(pattern, infos)
    title = result.group(2) if result is not None else ''
    
    # Track number
    pattern = r'(track|Track|TRACK)\s*:\s*(\d+)\s*[^\n\r]+'
    result = re.search(pattern, infos)
    track_num = int(result.group(2)) if result is not None else 0
    
    return bitrate, artist, album, title, track_num

app = wx.App()
frame = MainFrame()
app.MainLoop()

import os
import hashlib
import threading
import ctypes
from ctypes import wintypes

import customtkinter as ctk
from tkinter import filedialog, messagebox


# ==========================================================
# APP SETTINGS
# ==========================================================

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

APP_WIDTH = 520
APP_HEIGHT = 900

BG = "#070B14"
CARD = "#101722"
CARD_2 = "#151E2D"

TEXT = "#F4F7FB"
MUTED = "#8290A6"

ACCENT = "#00D4FF"
SUCCESS = "#22C55E"
WARNING = "#F59E0B"
DANGER = "#EF4444"


# ==========================================================
# WINDOWS RECYCLE BIN SETTINGS
# ==========================================================

FO_DELETE = 3

FOF_SILENT = 0x0004
FOF_NOCONFIRMATION = 0x0010
FOF_ALLOWUNDO = 0x0040
FOF_NOERRORUI = 0x0400


class SHFILEOPSTRUCTW(ctypes.Structure):

    _fields_ = [
        ("hwnd", wintypes.HWND),
        ("wFunc", wintypes.UINT),
        ("pFrom", wintypes.LPCWSTR),
        ("pTo", wintypes.LPCWSTR),
        ("fFlags", ctypes.c_ushort),
        ("fAnyOperationsAborted", wintypes.BOOL),
        ("hNameMappings", ctypes.c_void_p),
        ("lpszProgressTitle", wintypes.LPCWSTR),
    ]


# ==========================================================
# MOVE FILE TO WINDOWS RECYCLE BIN
# ==========================================================

def move_to_recycle_bin(file_path):

    absolute_path = os.path.abspath(file_path)

    # SHFileOperation requires double-null terminated path
    source = absolute_path + "\0\0"

    operation = SHFILEOPSTRUCTW()

    operation.hwnd = None
    operation.wFunc = FO_DELETE
    operation.pFrom = source
    operation.pTo = None

    operation.fFlags = (
        FOF_ALLOWUNDO
        | FOF_NOCONFIRMATION
        | FOF_SILENT
        | FOF_NOERRORUI
    )

    operation.fAnyOperationsAborted = False
    operation.hNameMappings = None
    operation.lpszProgressTitle = None

    result = ctypes.windll.shell32.SHFileOperationW(
        ctypes.byref(operation)
    )

    return (
        result == 0
        and not operation.fAnyOperationsAborted
    )


# ==========================================================
# DUPLICATE FILE FINDER APP
# ==========================================================

class DuplicateFinderApp(ctk.CTk):

    def __init__(self):

        super().__init__()

        self.title("Duplicate File Finder Pro")

        self.geometry(
            f"{APP_WIDTH}x{APP_HEIGHT}"
        )

        self.resizable(False, False)

        self.configure(
            fg_color=BG
        )

        self.selected_folder = ""

        self.duplicate_groups = []

        self.file_checkboxes = []

        self.is_scanning = False

        self.create_ui()


    # ======================================================
    # CREATE UI
    # ======================================================

    def create_ui(self):

        # ==================================================
        # HEADER
        # ==================================================

        header = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        header.pack(
            fill="x",
            padx=24,
            pady=(22, 10)
        )


        ctk.CTkLabel(
            header,
            text="DUPLICATE",
            font=ctk.CTkFont(
                size=30,
                weight="bold"
            ),
            text_color=TEXT
        ).pack(
            anchor="w"
        )


        ctk.CTkLabel(
            header,
            text="FILE FINDER",
            font=ctk.CTkFont(
                size=30,
                weight="bold"
            ),
            text_color=ACCENT
        ).pack(
            anchor="w"
        )


        ctk.CTkLabel(
            header,
            text="Find hidden duplicate files wasting your storage",
            font=ctk.CTkFont(
                size=13
            ),
            text_color=MUTED
        ).pack(
            anchor="w",
            pady=(4, 0)
        )


        # ==================================================
        # FOLDER CARD
        # ==================================================

        folder_card = ctk.CTkFrame(
            self,
            fg_color=CARD,
            corner_radius=18
        )

        folder_card.pack(
            fill="x",
            padx=24,
            pady=10
        )


        ctk.CTkLabel(
            folder_card,
            text="SCAN LOCATION",
            font=ctk.CTkFont(
                size=12,
                weight="bold"
            ),
            text_color=MUTED
        ).pack(
            anchor="w",
            padx=18,
            pady=(16, 6)
        )


        self.folder_label = ctk.CTkLabel(
            folder_card,
            text="No folder selected",
            font=ctk.CTkFont(
                size=13
            ),
            text_color=TEXT,
            anchor="w"
        )

        self.folder_label.pack(
            fill="x",
            padx=18
        )


        self.select_button = ctk.CTkButton(
            folder_card,
            text="SELECT FOLDER",
            height=44,
            corner_radius=12,
            fg_color=CARD_2,
            hover_color="#202C40",
            command=self.select_folder
        )

        self.select_button.pack(
            fill="x",
            padx=18,
            pady=(12, 16)
        )


        # ==================================================
        # SCAN BUTTON
        # ==================================================

        self.scan_button = ctk.CTkButton(
            self,
            text="SCAN FILES",
            height=56,
            corner_radius=16,
            font=ctk.CTkFont(
                size=17,
                weight="bold"
            ),
            fg_color=ACCENT,
            hover_color="#00A8CC",
            text_color="#00151C",
            command=self.start_scan
        )

        self.scan_button.pack(
            fill="x",
            padx=24,
            pady=10
        )


        # ==================================================
        # PROGRESS BAR
        # ==================================================

        self.progress = ctk.CTkProgressBar(
            self,
            height=10,
            corner_radius=10,
            progress_color=ACCENT
        )

        self.progress.pack(
            fill="x",
            padx=24,
            pady=(5, 5)
        )

        self.progress.set(0)


        self.status_label = ctk.CTkLabel(
            self,
            text="READY TO SCAN",
            text_color=MUTED,
            font=ctk.CTkFont(
                size=12,
                weight="bold"
            )
        )

        self.status_label.pack()


        # ==================================================
        # STATISTICS
        # ==================================================

        stats = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        stats.pack(
            fill="x",
            padx=24,
            pady=12
        )

        stats.grid_columnconfigure(
            (0, 1, 2),
            weight=1
        )


        self.files_value = self.create_stat_card(
            stats,
            0,
            "0",
            "FILES"
        )


        self.groups_value = self.create_stat_card(
            stats,
            1,
            "0",
            "DUPLICATES"
        )


        self.storage_value = self.create_stat_card(
            stats,
            2,
            "0 B",
            "WASTED"
        )


        # ==================================================
        # RESULTS HEADER
        # ==================================================

        result_header = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        result_header.pack(
            fill="x",
            padx=24,
            pady=(5, 5)
        )


        ctk.CTkLabel(
            result_header,
            text="DUPLICATE FILES",
            font=ctk.CTkFont(
                size=14,
                weight="bold"
            ),
            text_color=TEXT
        ).pack(
            side="left"
        )


        self.result_count = ctk.CTkLabel(
            result_header,
            text="0 FOUND",
            font=ctk.CTkFont(
                size=11,
                weight="bold"
            ),
            text_color=ACCENT
        )

        self.result_count.pack(
            side="right"
        )


        # ==================================================
        # RESULTS FRAME
        # ==================================================

        self.results_frame = ctk.CTkScrollableFrame(
            self,
            fg_color=CARD,
            corner_radius=16,
            height=310
        )

        self.results_frame.pack(
            fill="both",
            expand=True,
            padx=24,
            pady=(0, 10)
        )


        self.show_empty_message()


        # ==================================================
        # DELETE BUTTON
        # ==================================================

        self.delete_button = ctk.CTkButton(
            self,
            text="MOVE SELECTED TO RECYCLE BIN",
            height=50,
            corner_radius=14,
            fg_color=DANGER,
            hover_color="#C92D3B",
            font=ctk.CTkFont(
                size=14,
                weight="bold"
            ),
            command=self.delete_selected
        )

        self.delete_button.pack(
            fill="x",
            padx=24,
            pady=(0, 22)
        )


    # ======================================================
    # CREATE STAT CARD
    # ======================================================

    def create_stat_card(
        self,
        parent,
        column,
        value,
        title
    ):

        card = ctk.CTkFrame(
            parent,
            fg_color=CARD,
            corner_radius=14
        )

        card.grid(
            row=0,
            column=column,
            sticky="ew",
            padx=4
        )


        value_label = ctk.CTkLabel(
            card,
            text=value,
            font=ctk.CTkFont(
                size=20,
                weight="bold"
            ),
            text_color=ACCENT
        )

        value_label.pack(
            pady=(14, 0)
        )


        ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(
                size=10,
                weight="bold"
            ),
            text_color=MUTED
        ).pack(
            pady=(0, 14)
        )


        return value_label


    # ======================================================
    # SELECT FOLDER
    # ======================================================

    def select_folder(self):

        if self.is_scanning:
            return


        folder = filedialog.askdirectory()


        if not folder:
            return


        self.selected_folder = folder


        display_path = folder


        if len(display_path) > 55:

            display_path = (
                "..."
                + display_path[-52:]
            )


        self.folder_label.configure(
            text=display_path
        )


        self.status_label.configure(
            text="FOLDER SELECTED",
            text_color=SUCCESS
        )


        self.progress.set(0)


    # ======================================================
    # START SCAN
    # ======================================================

    def start_scan(self):

        if self.is_scanning:
            return


        if not self.selected_folder:

            messagebox.showwarning(
                "Folder Required",
                "Please select a folder first."
            )

            return


        if not os.path.isdir(
            self.selected_folder
        ):

            messagebox.showerror(
                "Invalid Folder",
                "The selected folder no longer exists."
            )

            return


        self.is_scanning = True


        self.scan_button.configure(
            state="disabled",
            text="SCANNING..."
        )


        self.select_button.configure(
            state="disabled"
        )


        self.delete_button.configure(
            state="disabled"
        )


        self.status_label.configure(
            text="DISCOVERING FILES...",
            text_color=WARNING
        )


        self.progress.set(0)


        self.files_value.configure(
            text="0"
        )

        self.groups_value.configure(
            text="0"
        )

        self.storage_value.configure(
            text="0 B"
        )

        self.result_count.configure(
            text="0 FOUND"
        )


        self.clear_results()


        scan_thread = threading.Thread(
            target=self.scan_folder,
            daemon=True
        )

        scan_thread.start()


    # ======================================================
    # SAFE UI UPDATE
    # ======================================================

    def update_progress(
        self,
        value,
        status=None
    ):

        value = max(
            0.0,
            min(
                1.0,
                value
            )
        )


        def update():

            self.progress.set(value)

            if status:

                self.status_label.configure(
                    text=status,
                    text_color=WARNING
                )


        self.after(
            0,
            update
        )


    # ======================================================
    # SCAN FOLDER
    # ======================================================

    def scan_folder(self):

        try:

            files = []


            # ==============================================
            # DISCOVER FILES
            # ==============================================

            for root, dirs, filenames in os.walk(
                self.selected_folder
            ):

                for filename in filenames:

                    path = os.path.join(
                        root,
                        filename
                    )


                    try:

                        if os.path.isfile(path):

                            files.append(path)

                    except (
                        PermissionError,
                        OSError
                    ):

                        continue


            total_files = len(files)


            if total_files == 0:

                self.after(
                    0,
                    lambda: self.scan_complete(
                        0,
                        [],
                        0
                    )
                )

                return


            # ==============================================
            # GROUP FILES BY SIZE
            # ==============================================

            size_groups = {}


            for index, path in enumerate(files):

                try:

                    size = os.path.getsize(path)

                    size_groups.setdefault(
                        size,
                        []
                    ).append(path)

                except (
                    PermissionError,
                    OSError
                ):

                    continue


                progress_value = (
                    (index + 1)
                    / total_files
                ) * 0.30


                self.update_progress(
                    progress_value,
                    f"ANALYZING FILES... {index + 1}/{total_files}"
                )


            # ==============================================
            # GET POSSIBLE DUPLICATES
            # ==============================================

            candidates = []


            for group in size_groups.values():

                if len(group) > 1:

                    candidates.extend(group)


            # ==============================================
            # HASH FILES
            # ==============================================

            hash_groups = {}

            candidate_total = len(candidates)


            if candidate_total == 0:

                self.after(
                    0,
                    lambda: self.scan_complete(
                        total_files,
                        [],
                        0
                    )
                )

                return


            for index, path in enumerate(candidates):

                try:

                    file_hash = self.calculate_hash(
                        path
                    )


                    # Use size + hash to avoid grouping
                    # unrelated edge cases

                    file_size = os.path.getsize(
                        path
                    )


                    key = (
                        file_size,
                        file_hash
                    )


                    hash_groups.setdefault(
                        key,
                        []
                    ).append(path)


                except (
                    PermissionError,
                    OSError
                ):

                    continue


                progress_value = (
                    0.30
                    +
                    (
                        (index + 1)
                        / candidate_total
                    )
                    * 0.70
                )


                self.update_progress(
                    progress_value,
                    f"CHECKING CONTENT... {index + 1}/{candidate_total}"
                )


            # ==============================================
            # FIND DUPLICATES
            # ==============================================

            duplicates = [

                group

                for group
                in hash_groups.values()

                if len(group) > 1

            ]


            # Sort largest duplicate groups first

            duplicates.sort(
                key=lambda group:
                self.safe_getsize(group[0])
                * (len(group) - 1),
                reverse=True
            )


            # ==============================================
            # CALCULATE WASTED SPACE
            # ==============================================

            wasted_space = 0


            for group in duplicates:

                file_size = self.safe_getsize(
                    group[0]
                )


                wasted_space += (
                    file_size
                    * (len(group) - 1)
                )


            self.duplicate_groups = duplicates


            self.after(
                0,
                lambda: self.scan_complete(
                    total_files,
                    duplicates,
                    wasted_space
                )
            )


        except Exception as error:

            error_message = str(error)


            self.after(
                0,
                lambda: self.scan_failed(
                    error_message
                )
            )


    # ======================================================
    # CALCULATE SHA-256 HASH
    # ======================================================

    @staticmethod
    def calculate_hash(path):

        sha256 = hashlib.sha256()


        with open(
            path,
            "rb"
        ) as file:

            while True:

                chunk = file.read(
                    1024 * 1024
                )


                if not chunk:
                    break


                sha256.update(chunk)


        return sha256.hexdigest()


    # ======================================================
    # SAFE GET FILE SIZE
    # ======================================================

    @staticmethod
    def safe_getsize(path):

        try:

            return os.path.getsize(path)

        except (
            PermissionError,
            OSError
        ):

            return 0


    # ======================================================
    # SCAN COMPLETE
    # ======================================================

    def scan_complete(
        self,
        total_files,
        duplicates,
        wasted_space
    ):

        self.is_scanning = False


        self.progress.set(1)


        duplicate_file_count = sum(

            len(group) - 1

            for group in duplicates

        )


        self.files_value.configure(
            text=str(total_files)
        )


        self.groups_value.configure(
            text=str(
                duplicate_file_count
            )
        )


        self.storage_value.configure(
            text=self.format_size(
                wasted_space
            )
        )


        self.result_count.configure(
            text=(
                f"{duplicate_file_count} FOUND"
            )
        )


        self.display_results(
            duplicates
        )


        if duplicate_file_count > 0:

            self.status_label.configure(
                text="DUPLICATE FILES DETECTED",
                text_color=DANGER
            )

        else:

            self.status_label.configure(
                text="NO DUPLICATES FOUND",
                text_color=SUCCESS
            )


        self.scan_button.configure(
            state="normal",
            text="SCAN AGAIN"
        )


        self.select_button.configure(
            state="normal"
        )


        self.delete_button.configure(
            state="normal"
        )


    # ======================================================
    # SCAN FAILED
    # ======================================================

    def scan_failed(
        self,
        error_message
    ):

        self.is_scanning = False


        self.status_label.configure(
            text="SCAN FAILED",
            text_color=DANGER
        )


        self.scan_button.configure(
            state="normal",
            text="SCAN FILES"
        )


        self.select_button.configure(
            state="normal"
        )


        self.delete_button.configure(
            state="normal"
        )


        messagebox.showerror(
            "Scan Error",
            "An error occurred while scanning:\n\n"
            + error_message
        )


    # ======================================================
    # DISPLAY RESULTS
    # ======================================================

    def display_results(
        self,
        duplicates
    ):

        self.clear_results()


        if not duplicates:

            self.show_empty_message()

            return


        for group_index, group in enumerate(
            duplicates,
            start=1
        ):

            if not group:
                continue


            group_card = ctk.CTkFrame(
                self.results_frame,
                fg_color=CARD_2,
                corner_radius=12
            )

            group_card.pack(
                fill="x",
                padx=4,
                pady=6
            )


            ctk.CTkLabel(
                group_card,
                text=(
                    f"DUPLICATE GROUP {group_index}"
                ),
                text_color=ACCENT,
                font=ctk.CTkFont(
                    size=11,
                    weight="bold"
                )
            ).pack(
                anchor="w",
                padx=12,
                pady=(10, 4)
            )


            # ==============================================
            # ORIGINAL FILE
            # ==============================================

            original = group[0]

            original_name = os.path.basename(
                original
            )


            ctk.CTkLabel(
                group_card,
                text=(
                    f"KEEP  •  {original_name}"
                ),
                text_color=SUCCESS,
                font=ctk.CTkFont(
                    size=12,
                    weight="bold"
                ),
                anchor="w"
            ).pack(
                fill="x",
                padx=12,
                pady=4
            )


            # ==============================================
            # DUPLICATE FILES
            # ==============================================

            for path in group[1:]:

                variable = ctk.BooleanVar(
                    value=True
                )


                filename = os.path.basename(
                    path
                )


                checkbox = ctk.CTkCheckBox(
                    group_card,
                    text=filename,
                    variable=variable,
                    text_color=TEXT,
                    hover_color=ACCENT,
                    fg_color=DANGER
                )


                checkbox.pack(
                    anchor="w",
                    padx=12,
                    pady=5
                )


                self.file_checkboxes.append(
                    (
                        variable,
                        path
                    )
                )


            ctk.CTkLabel(
                group_card,
                text=(
                    f"{len(group)} COPIES  •  "
                    f"{self.format_size(self.safe_getsize(original))} EACH"
                ),
                text_color=MUTED,
                font=ctk.CTkFont(
                    size=10
                )
            ).pack(
                anchor="e",
                padx=12,
                pady=(2, 10)
            )


    # ======================================================
    # DELETE SELECTED FILES
    # ======================================================

    def delete_selected(self):

        if self.is_scanning:
            return


        selected = [

            path

            for variable, path
            in self.file_checkboxes

            if (
                variable.get()
                and os.path.exists(path)
            )

        ]


        if not selected:

            messagebox.showinfo(
                "Nothing Selected",
                "Select duplicate files first."
            )

            return


        selected_size = sum(

            self.safe_getsize(path)

            for path in selected

        )


        confirm = messagebox.askyesno(
            "Confirm Cleanup",
            (
                f"Move {len(selected)} duplicate file(s) "
                f"to the Recycle Bin?\n\n"
                f"Storage to recover: "
                f"{self.format_size(selected_size)}"
            )
        )


        if not confirm:
            return


        self.delete_button.configure(
            state="disabled",
            text="MOVING FILES..."
        )


        self.scan_button.configure(
            state="disabled"
        )


        self.select_button.configure(
            state="disabled"
        )


        delete_thread = threading.Thread(
            target=self.delete_files_worker,
            args=(selected,),
            daemon=True
        )

        delete_thread.start()


    # ======================================================
    # DELETE FILES WORKER
    # ======================================================

    def delete_files_worker(
        self,
        selected
    ):

        deleted = 0

        failed = 0


        for path in selected:

            try:

                if os.path.exists(path):

                    success = move_to_recycle_bin(
                        path
                    )


                    if success:

                        deleted += 1

                    else:

                        failed += 1


            except Exception:

                failed += 1


        self.after(
            0,
            lambda: self.delete_complete(
                deleted,
                failed
            )
        )


    # ======================================================
    # DELETE COMPLETE
    # ======================================================

    def delete_complete(
        self,
        deleted,
        failed
    ):

        self.delete_button.configure(
            state="normal",
            text="MOVE SELECTED TO RECYCLE BIN"
        )


        self.scan_button.configure(
            state="normal"
        )


        self.select_button.configure(
            state="normal"
        )


        if failed == 0:

            messagebox.showinfo(
                "Storage Cleanup Complete",
                (
                    f"{deleted} duplicate file(s) "
                    f"moved to the Recycle Bin."
                )
            )

        else:

            messagebox.showwarning(
                "Cleanup Complete",
                (
                    f"Moved: {deleted}\n"
                    f"Failed: {failed}"
                )
            )


        # Rescan automatically

        self.start_scan()


    # ======================================================
    # CLEAR RESULTS
    # ======================================================

    def clear_results(self):

        for widget in (
            self.results_frame.winfo_children()
        ):

            widget.destroy()


        self.file_checkboxes.clear()


    # ======================================================
    # EMPTY MESSAGE
    # ======================================================

    def show_empty_message(self):

        ctk.CTkLabel(
            self.results_frame,
            text=(
                "\nSELECT A FOLDER AND START SCANNING\n\n"
                "Duplicate files will appear here."
            ),
            font=ctk.CTkFont(
                size=13,
                weight="bold"
            ),
            text_color=MUTED
        ).pack(
            pady=55
        )


    # ======================================================
    # FORMAT FILE SIZE
    # ======================================================

    @staticmethod
    def format_size(size):

        units = [
            "B",
            "KB",
            "MB",
            "GB",
            "TB"
        ]


        size = float(
            max(
                size,
                0
            )
        )


        for unit in units:

            if size < 1024:

                if unit == "B":

                    return (
                        f"{int(size)} {unit}"
                    )


                return (
                    f"{size:.1f} {unit}"
                )


            size /= 1024


        return f"{size:.1f} PB"


# ==========================================================
# RUN APPLICATION
# ==========================================================

if __name__ == "__main__":

    app = DuplicateFinderApp()

    app.mainloop()
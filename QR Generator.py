import tkinter as tk
from tkinter import ttk, messagebox, filedialog, colorchooser
import qrcode
from PIL import Image, ImageTk
import qrcode.image.styledpil
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import SquareModuleDrawer, RoundedModuleDrawer, CircleModuleDrawer

class QRCodeGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("QR Code Generator")

        self.label_data = ttk.Label(root, text="输入数据:")
        self.label_data.grid(row=0, column=0, pady=10, padx=10, sticky=tk.W)
        self.entry_data = ttk.Entry(root, width=30)
        self.entry_data.grid(row=0, column=1, pady=10, padx=10, sticky=tk.W)

        self.content_type_var = tk.StringVar(value="Text")
        self.label_content_type = ttk.Label(root, text="内容类型:")
        self.label_content_type.grid(row=1, column=0, pady=5, padx=10, sticky=tk.W)
        self.combo_content_type = ttk.Combobox(root, textvariable=self.content_type_var,
                                               values=["Text", "URL", "Email", "Phone"], state="readonly")
        self.combo_content_type.grid(row=1, column=1, pady=5, padx=10, sticky=tk.W)

        self.label_size = ttk.Label(root, text="尺寸(0-300):")
        self.label_size.grid(row=2, column=0, pady=5, padx=10, sticky=tk.W)
        self.entry_size = ttk.Entry(root, width=10)
        self.entry_size.grid(row=2, column=1, pady=5, padx=10, sticky=tk.W)

        self.color_var = tk.StringVar(value="white")
        self.color_label = ttk.Label(root, text="选择颜色:")
        self.color_label.grid(row=3, column=0, pady=5, padx=10, sticky=tk.W)
        self.color_button = tk.Button(root, text="选择颜色", command=self.choose_color, bg=self.color_var.get())
        self.color_button.grid(row=3, column=1, pady=5, padx=10, sticky=tk.W)

        self.error_correction_var = tk.StringVar(value="L")
        self.label_correction = ttk.Label(root, text="纠错级别:")
        self.label_correction.grid(row=4, column=0, pady=5, padx=10, sticky=tk.W)
        self.combo_correction = ttk.Combobox(root, textvariable=self.error_correction_var,
                                             values=["L", "M", "Q", "H"], state="readonly")
        self.combo_correction.grid(row=4, column=1, pady=5, padx=10, sticky=tk.W)

        self.style_var = tk.StringVar(value="Square")
        self.label_style = ttk.Label(root, text="二维码样式:")
        self.label_style.grid(row=5, column=0, pady=5, padx=10, sticky=tk.W)
        self.combo_style = ttk.Combobox(root, textvariable=self.style_var,
                                        values=["Square", "Rounded", "Dots"], state="readonly")
        self.combo_style.grid(row=5, column=1, pady=5, padx=10, sticky=tk.W)

        self.batch_mode_var = tk.BooleanVar(value=False)
        self.batch_mode_checkbox = ttk.Checkbutton(root, text="启用批量生成",
                                                   variable=self.batch_mode_var,
                                                   command=self.toggle_batch_mode)
        self.batch_mode_checkbox.grid(row=6, column=0, columnspan=2, pady=5)

        self.label_batch = ttk.Label(root, text="批量数据(英文逗号分隔):")
        self.entry_batch = ttk.Entry(root, width=30)
        self.batch_generate_button = ttk.Button(root, text="批量生成", command=self.batch_generate_qr_codes)

        self.generate_button = ttk.Button(root, text="生成QR码", command=self.generate_qr_code)
        self.generate_button.grid(row=7, column=0, columnspan=2, pady=10)

        self.label_qr_code = ttk.Label(root, text="生成的QR码:")
        self.label_qr_code.grid(row=8, column=0, pady=5, padx=10, sticky=tk.W)
        self.canvas_qr_code = tk.Canvas(root, width=500, height=300)
        self.canvas_qr_code.grid(row=9, column=0, columnspan=2, pady=10)

        self.add_logo_var = tk.BooleanVar(value=False)
        self.add_logo_checkbox = ttk.Checkbutton(root, text="添加徽标", variable=self.add_logo_var)
        self.add_logo_checkbox.grid(row=10, column=0, columnspan=2, pady=10)

        self.save_button = ttk.Button(root, text="保存QR码", command=self.save_qr_code)
        self.save_button.grid(row=11, column=0, columnspan=2, pady=10)

        self.qr_code_label = ttk.Label(root)

        self.error_correction_map = {
            "L": qrcode.constants.ERROR_CORRECT_L,
            "M": qrcode.constants.ERROR_CORRECT_M,
            "Q": qrcode.constants.ERROR_CORRECT_Q,
            "H": qrcode.constants.ERROR_CORRECT_H
        }

        self.style_map = {
            "Square": SquareModuleDrawer(),
            "Rounded": RoundedModuleDrawer(),
            "Dots": CircleModuleDrawer()
        }

    def toggle_batch_mode(self):
        if self.batch_mode_var.get():
            self.label_batch.grid(row=6, column=0, pady=5, padx=10, sticky=tk.W)
            self.entry_batch.grid(row=6, column=1, pady=5, padx=10, sticky=tk.W)
            self.batch_generate_button.grid(row=7, column=0, columnspan=2, pady=10)
        else:
            self.label_batch.grid_remove()
            self.entry_batch.grid_remove()
            self.batch_generate_button.grid_remove()

    def format_data(self, data, content_type):
        if content_type == "URL" and not data.startswith(('http://', 'https://')):
            data = 'https://' + data
        elif content_type == "Email":
            data = f'mailto:{data}'
        elif content_type == "Phone":
            data = f'tel:{data}'
        return data

    def generate_qr_code(self):
        try:
            data = self.entry_data.get()
            content_type = self.content_type_var.get()
            data = self.format_data(data, content_type)
            size = int(self.entry_size.get() or 300)
            error_correction = self.error_correction_map[self.error_correction_var.get()]
            color = self.color_var.get()
            style = self.style_map[self.style_var.get()]

            qr = qrcode.QRCode(
                version=1,
                error_correction=error_correction,
                box_size=10,
                border=3,
            )
            qr.add_data(data)
            qr.make(fit=True)

            # 1) 先拿到纯黑白的二维码（RGBA）
            img = qr.make_image(
                image_factory=StyledPilImage,
                module_drawer=style
            ).convert("RGBA")

            # 2) 把黑色替换成用户选的颜色
            r, g, b = tuple(int(color.lstrip('#')[i:i + 2], 16) for i in (0, 2, 4))
            data = img.getdata()
            new_data = [
                (r, g, b, 255) if item[:3] == (0, 0, 0) else item
                for item in data
            ]
            img.putdata(new_data)

            if self.add_logo_var.get():
                self.add_logo(img)

            img = img.resize((size, size))

            self.qr_code_label = ImageTk.PhotoImage(img)
            canvas_width = self.canvas_qr_code.winfo_width()
            canvas_height = self.canvas_qr_code.winfo_height()
            x = (canvas_width - size) // 2
            y = (canvas_height - size) // 2
            self.canvas_qr_code.delete("all")
            self.canvas_qr_code.create_image(x, y, anchor=tk.NW, image=self.qr_code_label)

        except Exception as e:
            messagebox.showerror("错误", f"生成QR码时发生错误: {str(e)}")

    def choose_color(self):
        color = colorchooser.askcolor()[1]
        if color:
            self.color_var.set(color)
            self.color_button.config(bg=color)
            self.generate_qr_code()


    def add_logo(self, img):
        logo_path = filedialog.askopenfilename(title="选择徽标文件",
                                               filetypes=[("Image files", "*.png;*.jpg;*.jpeg")])
        if logo_path:
            logo_img = Image.open(logo_path)
            logo_img = logo_img.resize((35, 35))
            position = ((img.size[0] - logo_img.size[0]) // 2, (img.size[1] - logo_img.size[1]) // 2)
            img.paste(logo_img, position)

    def save_qr_code(self):
        file_name = filedialog.asksaveasfilename(defaultextension=".png",
                                                 filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg")],
                                                 title="保存二维码")
        if not file_name:
            return
        try:
            img = ImageTk.getimage(self.qr_code_label)
            img.save(file_name)
            self.show_info("二维码已成功保存")
        except Exception as e:
            self.show_error(f"保存失败: {str(e)}")

    def batch_generate_qr_codes(self):
        try:
            batch_data = self.entry_batch.get()
            if not batch_data:
                messagebox.showerror("错误", "请输入批量生成的数据")
                return
            data_list = batch_data.split(",")
            size = int(self.entry_size.get() or 300)
            color = self.color_var.get()
            error_correction = self.error_correction_map[self.error_correction_var.get()]
            style = self.style_map[self.style_var.get()]
            content_type = self.content_type_var.get()

            for data in data_list:
                data = self.format_data(data.strip(), content_type)
                qr = qrcode.QRCode(
                    version=1,
                    error_correction=error_correction,
                    box_size=10,
                    border=4,
                )
                qr.add_data(data)
                qr.make(fit=True)
                from PIL import ImageOps

                # 生成二维码图像
                img = qr.make_image(
                    image_factory=StyledPilImage,
                    module_drawer=style
                ).convert("RGBA")  # 转为 RGBA 以便处理透明

                # 替换黑色模块为你选择的颜色
                data = img.getdata()
                new_data = []
                for item in data:
                    if item[:3] == (0, 0, 0):  # 黑色模块
                        new_data.append(
                            tuple(int(self.color_var.get().lstrip('#')[i:i + 2], 16) for i in (0, 2, 4)) + (255,))
                    else:
                        new_data.append(item)
                img.putdata(new_data)
                img = img.resize((size, size))
                if self.add_logo_var.get():
                    self.add_logo(img)
                img.save(f"qr_code_{data}.png")
            self.show_info("批量生成完成，图片已自动保存至本文件夹")
        except Exception as e:
            messagebox.showerror("错误", f"批量生成失败: {str(e)}")

    def show_error(self, message):
        messagebox.showerror("错误", message)

    def show_info(self, message):
        messagebox.showinfo("提示", message)

if __name__ == "__main__":
    root = tk.Tk()
    app = QRCodeGeneratorApp(root)
    root.mainloop()

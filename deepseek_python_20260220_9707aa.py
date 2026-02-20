import discord
from discord.ext import commands
import asyncio
import random
from datetime import datetime

# ========== CẤU HÌNH ==========
BOT_TOKEN = "MTQ3NDIxNTA3MDc1Mjk2NDY2OA.Gy2KMs.WKB6RO356dnn66cnttU0vYyN8Ilo5CQ81JC2M0"
PREFIX = "!"
SPEED = 0.5  # Tốc độ gửi (giây)

# ========== INTENTS ==========
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# ========== CLASS BOT ==========
class SpamDMBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=PREFIX, intents=intents)
        self.insults = []  # Câu chửi
        self.images = []   # Link ảnh
        self.insult_index = 0
        self.image_index = 0
        
    async def setup_hook(self):
        await self.tree.sync()
        print("✅ Đã sync slash commands")

bot = SpamDMBot()

# ========== ĐỌC FILE ==========
def load_insults():
    try:
        with open("noi_dung.txt", 'r', encoding='utf-8') as f:
            lines = f.readlines()
            return [line.strip() for line in lines if line.strip()]
    except:
        # Tạo file mẫu nếu chưa có
        sample = [
            "ĐỊT MẸ MÀY",
            "THẰNG NGU HỌC", 
            "ÓC CHÓ VỪA THÔI",
            "MÀY BỊ KHÙNG À?",
            "CÂU CHỬI SỐ 1",
            "CÂU CHỬI SỐ 2",
            "CÂU CHỬI SỐ 3",
        ]
        with open("noi_dung.txt", 'w', encoding='utf-8') as f:
            f.write('\n'.join(sample))
        return sample

def load_images():
    try:
        with open("anh.txt", 'r', encoding='utf-8') as f:
            lines = f.readlines()
            return [line.strip() for line in lines if line.strip() and line.strip().startswith('http')]
    except:
        # Tạo file mẫu nếu chưa có
        sample = [
            "https://i.imgur.com/1.jpg",
            "https://i.imgur.com/2.jpg", 
            "https://i.imgur.com/3.jpg",
        ]
        with open("anh.txt", 'w', encoding='utf-8') as f:
            f.write('\n'.join(sample))
        return sample

bot.insults = load_insults()
bot.images = load_images()

# ========== LỆNH SPAM DM 1 NGƯỜI ==========
@bot.tree.command(name="spam", description="Spam DM 1 người")
async def spam_dm(interaction: discord.Interaction, nguoi_dung: discord.Member, so_lan: int):
    """
    Spam DM 1 người dùng
    - nguoi_dung: @tag người cần spam
    - so_lan: số lần spam (1-100)
    """
    
    # Kiểm tra số lần hợp lệ
    if so_lan > 100:
        await interaction.response.send_message("❌ Chỉ được spam tối đa 100 lần!")
        return
    
    if so_lan < 1:
        await interaction.response.send_message("❌ Số lần phải lớn hơn 0!")
        return
    
    await interaction.response.send_message(f"📨 **ĐANG SPAM {nguoi_dung.mention} {so_lan} LẦN**")
    
    success = 0
    for i in range(so_lan):
        try:
            # Lấy nội dung từ file (luân phiên)
            noi_dung = bot.insults[i % len(bot.insults)]
            
            # Tạo embed
            embed = discord.Embed(
                title=f"💢 TIN NHẮN {i+1}/{so_lan}",
                description=f"# {noi_dung}\n👉 {nguoi_dung.mention} 👈",
                color=discord.Color.red(),
                timestamp=datetime.now()
            )
            
            # Thêm ảnh nếu có
            if bot.images:
                anh = bot.images[i % len(bot.images)]
                embed.set_image(url=anh)
            
            # Gửi tin nhắn
            await nguoi_dung.send(embed=embed)
            success += 1
            
            # Chờ 1 chút để tránh rate limit
            await asyncio.sleep(SPEED)
            
        except discord.Forbidden:
            # Người dùng đã tắt DM
            await interaction.followup.send(f"⚠️ {nguoi_dung.mention} đã tắt DM!")
            break
        except Exception as e:
            print(f"Lỗi: {e}")
            continue
    
    # Gửi báo cáo
    await interaction.followup.send(f"✅ **HOÀN TẤT!** Đã gửi {success}/{so_lan} tin nhắn")

# ========== LỆNH SPAM DM TẤT CẢ ==========
@bot.tree.command(name="spamall", description="Spam DM tất cả member trong server")
async def spam_all(interaction: discord.Interaction, so_lan: int):
    """
    Spam DM tất cả member
    - so_lan: số lần spam mỗi người (1-20)
    """
    
    # Kiểm tra số lần hợp lệ
    if so_lan > 20:
        await interaction.response.send_message("❌ Chỉ được spam tối đa 20 lần mỗi người!")
        return
    
    if so_lan < 1:
        await interaction.response.send_message("❌ Số lần phải lớn hơn 0!")
        return
    
    # Lấy danh sách member (không bao gồm bot)
    members = [m for m in interaction.guild.members if not m.bot]
    
    await interaction.response.send_message(f"📨 **ĐANG SPAM {len(members)} NGƯỜI, {so_lan} LẦN/NGƯỜI**")
    
    total_success = 0
    total_failed = 0
    
    for member in members:
        member_success = 0
        
        for i in range(so_lan):
            try:
                # Lấy nội dung và ảnh
                noi_dung = bot.insults[(i + member_success) % len(bot.insults)]
                
                # Tạo embed
                embed = discord.Embed(
                    title=f"💢 TIN NHẮN CHO {member.name} - LẦN {i+1}",
                    description=f"# {noi_dung}\n👉 {member.mention} 👈",
                    color=discord.Color.red()
                )
                
                if bot.images:
                    anh = bot.images[(i + member_success) % len(bot.images)]
                    embed.set_image(url=anh)
                
                await member.send(embed=embed)
                member_success += 1
                await asyncio.sleep(SPEED / 2)  # Nhanh hơn 1 chút
                
            except:
                total_failed += 1
                continue
        
        total_success += member_success
        
        # Thông báo tiến độ mỗi 5 người
        if len(members) > 10 and (members.index(member) + 1) % 5 == 0:
            await interaction.followup.send(f"⏳ Đã xử lý {members.index(member) + 1}/{len(members)} người...")
        
        await asyncio.sleep(SPEED)
    
    # Gửi báo cáo
    await interaction.followup.send(
        f"✅ **HOÀN TẤT!**\n"
        f"📊 **THỐNG KÊ:**\n"
        f"👥 Số người: {len(members)}\n"
        f"📨 Gửi thành công: {total_success}\n"
        f"❌ Gửi thất bại: {total_failed}"
    )

# ========== LỆNH SPAM TÙY CHỈNH ==========
@bot.tree.command(name="spamcustom", description="Spam DM với nội dung tự nhập")
async def spam_custom(
    interaction: discord.Interaction, 
    nguoi_dung: discord.Member, 
    so_lan: int, 
    noi_dung: str
):
    """
    Spam DM với nội dung tự nhập
    - nguoi_dung: @tag người cần spam
    - so_lan: số lần spam
    - noi_dung: nội dung muốn gửi
    """
    
    if so_lan > 50:
        await interaction.response.send_message("❌ Chỉ được spam tối đa 50 lần!")
        return
    
    await interaction.response.send_message(f"📨 **ĐANG SPAM {nguoi_dung.mention} {so_lan} LẦN**")
    
    success = 0
    for i in range(so_lan):
        try:
            embed = discord.Embed(
                title=f"💢 TIN NHẮN {i+1}/{so_lan}",
                description=f"# {noi_dung}\n👉 {nguoi_dung.mention} 👈",
                color=discord.Color.red()
            )
            await nguoi_dung.send(embed=embed)
            success += 1
            await asyncio.sleep(SPEED)
        except:
            await interaction.followup.send(f"⚠️ Không thể gửi cho {nguoi_dung.mention}")
            break
    
    await interaction.followup.send(f"✅ Đã gửi {success}/{so_lan} tin")

# ========== LỆNH QUẢN LÝ NỘI DUNG ==========
@bot.tree.command(name="themnoi dung", description="Thêm câu chửi mới vào file")
async def them_noi_dung(interaction: discord.Interaction, noi_dung: str):
    with open("noi_dung.txt", 'a', encoding='utf-8') as f:
        f.write(f"\n{noi_dung}")
    
    bot.insults = load_insults()
    await interaction.response.send_message(f"✅ Đã thêm! Hiện có {len(bot.insults)} câu")

@bot.tree.command(name="themanh", description="Thêm link ảnh mới vào file")
async def them_anh(interaction: discord.Interaction, link: str):
    with open("anh.txt", 'a', encoding='utf-8') as f:
        f.write(f"\n{link}")
    
    bot.images = load_images()
    await interaction.response.send_message(f"✅ Đã thêm! Hiện có {len(bot.images)} ảnh")

@bot.tree.command(name="list", description="Xem danh sách nội dung")
async def list_content(interaction: discord.Interaction):
    msg = f"**📁 DANH SÁCH HIỆN TẠI:**\n"
    msg += f"📝 Câu chửi: {len(bot.insults)} câu\n"
    msg += f"🖼️ Ảnh: {len(bot.images)} ảnh\n\n"
    
    if bot.insults:
        msg += "**📝 5 CÂU ĐẦU TIÊN:**\n"
        for i, insult in enumerate(bot.insults[:5]):
            msg += f"{i+1}. {insult[:50]}{'...' if len(insult) > 50 else ''}\n"
    
    await interaction.response.send_message(msg)

@bot.tree.command(name="speed", description="Chỉnh tốc độ gửi tin (giây)")
async def set_speed(interaction: discord.Interaction, giay: float):
    global SPEED
    if giay < 0.1:
        await interaction.response.send_message("⚠️ Tốc độ tối thiểu 0.1 giây")
        return
    
    SPEED = giay
    await interaction.response.send_message(f"⚡ Đã đặt tốc độ: {giay} giây")

@bot.tree.command(name="help", description="Hướng dẫn sử dụng")
async def help_command(interaction: discord.Interaction):
    help_text = f"""
**🤖 BOT SPAM DM ULTIMATE**

**📨 CÁC LỆNH SPAM:**
`/spam @người_dùng 10` - Spam DM 1 người
`/spamall 5` - Spam DM tất cả member
`/spamcustom @người_dùng 5 "Nội dung"` - Spam với nội dung tự nhập

**📝 QUẢN LÝ NỘI DUNG:**
`/themnoi dung "Câu chửi mới"` - Thêm câu chửi
`/themanh "https://link.anh.jpg"` - Thêm link ảnh
`/list` - Xem danh sách
`/speed 0.5` - Chỉnh tốc độ

**📊 THÔNG TIN:**
📝 Câu chửi: {len(bot.insults)}
🖼️ Ảnh: {len(bot.images)}
⚡ Tốc độ: {SPEED}s

**⚠️ LƯU Ý:**
- Không spam quá nhiều để tránh rate limit
- Nội dung được lấy từ file `noi_dung.txt` và `anh.txt`
- Mỗi lần gửi sẽ tự động luân phiên nội dung
    """
    await interaction.response.send_message(help_text)

# ========== READY ==========
@bot.event
async def on_ready():
    print("="*50)
    print("🤖 BOT SPAM DM ĐÃ CHẠY!")
    print(f"📝 Tên bot: {bot.user.name}")
    print(f"📁 Câu chửi: {len(bot.insults)}")
    print(f"🖼️ Ảnh: {len(bot.images)}")
    print(f"⚡ Tốc độ: {SPEED}s")
    print("="*50)
    print("📢 LỆNH: /help")
    print("="*50)

# ========== CHẠY BOT ==========
if __name__ == "__main__":
    bot.run(BOT_TOKEN)
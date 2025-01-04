# Enhance the slide design for a hackathon presentation

# Create a new presentation object
prs = Presentation()
slide_layout = prs.slide_layouts[6]  # Choosing a blank layout
slide = prs.slides.add_slide(slide_layout)

# Add a title with a dynamic and bold style
title_shape = slide.shapes.add_textbox(Inches(0.5), Inches(0.5), Inches(9), Inches(1))
title_frame = title_shape.text_frame
title_frame.text = "Ideas and Approach Details"
title_paragraph = title_frame.paragraphs[0]
title_paragraph.font.size = Pt(40)  # Large title font
title_paragraph.font.bold = True
title_paragraph.font.color.rgb = RGBColor(0, 102, 204)  # Bright blue

# Add content with a modern layout
content_shape = slide.shapes.add_textbox(Inches(5), Inches(1.5), Inches(4), Inches(5))
content_frame = content_shape.text_frame
content_frame.word_wrap = True  # Ensure text wraps within the text box

# Use short, impactful bullet points for hackathon clarity
content = [
    "🚀 Problem: Interactive problem-solving tool needed.",
    "🎯 Goal: Dynamic & visual web-based math solutions.",
    "✨ Features:",
    "- Step-by-step solutions.",
    "- Graphing equations interactively.",
    "- Covers equations, differentiation, integration, and inequalities.",
    "🌟 Impact: Simplifies math for students & educators."
]
for point in content:
    p = content_frame.add_paragraph()
    p.text = point
    p.font.size = Pt(18)  # Medium font for readability
    if point.startswith("✨") or point.startswith("🌟"):
        p.font.bold = True  # Highlight key sections

# Add an improved JPEG image for visual impact
slide.shapes.add_picture(jpeg_image_path, Inches(0.5), Inches(1.5), height=Inches(5))

# Save the improved slide
pptx_path = "/mnt/data/Hackathon_Slide_1.pptx"
prs.save(pptx_path)

pptx_path

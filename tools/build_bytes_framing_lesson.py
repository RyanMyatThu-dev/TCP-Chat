"""Build the byte handling and TCP framing lesson PDF."""

from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.graphics.shapes import Drawing, Line, Polygon, Rect, String
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import mm
from reportlab.platypus import (
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "output" / "pdf" / "python-bytes-and-tcp-framing-lesson.pdf"

NAVY = colors.HexColor("#17324D")
BLUE = colors.HexColor("#2574A9")
TEAL = colors.HexColor("#17807B")
GREEN = colors.HexColor("#2F855A")
ORANGE = colors.HexColor("#C26723")
RED = colors.HexColor("#B64545")
INK = colors.HexColor("#24303A")
MUTED = colors.HexColor("#64727D")
LINE = colors.HexColor("#CFDCE5")
PALE_BLUE = colors.HexColor("#EAF3F8")
PALE_TEAL = colors.HexColor("#E7F5F3")
PALE_ORANGE = colors.HexColor("#FFF1E5")
PALE_RED = colors.HexColor("#FBECEC")
PALE_GREEN = colors.HexColor("#EAF6EF")
WHITE = colors.white

SANS = "LessonSans"
SANS_BOLD = "LessonSans-Bold"
MONO = "LessonMono"

pdfmetrics.registerFont(TTFont(SANS, "/usr/share/fonts/noto/NotoSans-Regular.ttf"))
pdfmetrics.registerFont(TTFont(SANS_BOLD, "/usr/share/fonts/noto/NotoSans-Bold.ttf"))
pdfmetrics.registerFont(TTFont(MONO, "/usr/share/fonts/noto/NotoSansMono-Regular.ttf"))


def styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "LessonTitle",
            parent=base["Title"],
            fontName=SANS_BOLD,
            fontSize=27,
            leading=32,
            textColor=NAVY,
            alignment=TA_CENTER,
            spaceAfter=8,
        ),
        "subtitle": ParagraphStyle(
            "LessonSubtitle",
            parent=base["Normal"],
            fontName=SANS,
            fontSize=12,
            leading=17,
            textColor=MUTED,
            alignment=TA_CENTER,
            spaceAfter=12,
        ),
        "section": ParagraphStyle(
            "Section",
            parent=base["Heading1"],
            fontName=SANS_BOLD,
            fontSize=19,
            leading=23,
            textColor=NAVY,
            spaceAfter=8,
        ),
        "h2": ParagraphStyle(
            "H2",
            parent=base["Heading2"],
            fontName=SANS_BOLD,
            fontSize=12.5,
            leading=16,
            textColor=BLUE,
            spaceBefore=6,
            spaceAfter=5,
            keepWithNext=True,
        ),
        "body": ParagraphStyle(
            "Body",
            parent=base["BodyText"],
            fontName=SANS,
            fontSize=9.5,
            leading=13.5,
            textColor=INK,
            spaceAfter=6,
        ),
        "small": ParagraphStyle(
            "Small",
            parent=base["BodyText"],
            fontName=SANS,
            fontSize=8.2,
            leading=11.5,
            textColor=MUTED,
            spaceAfter=4,
        ),
        "bullet": ParagraphStyle(
            "Bullet",
            parent=base["BodyText"],
            fontName=SANS,
            fontSize=9.2,
            leading=13,
            textColor=INK,
            leftIndent=13,
            firstLineIndent=-7,
            spaceAfter=3,
        ),
        "code": ParagraphStyle(
            "Code",
            parent=base["Code"],
            fontName=MONO,
            fontSize=8.1,
            leading=11,
            textColor=INK,
            backColor=PALE_BLUE,
            borderColor=LINE,
            borderWidth=0.6,
            borderPadding=7,
            leftIndent=4,
            rightIndent=4,
            spaceBefore=4,
            spaceAfter=7,
        ),
        "callout": ParagraphStyle(
            "Callout",
            parent=base["BodyText"],
            fontName=SANS_BOLD,
            fontSize=10,
            leading=14,
            textColor=NAVY,
            backColor=PALE_TEAL,
            borderColor=TEAL,
            borderWidth=0.8,
            borderPadding=8,
            spaceBefore=4,
            spaceAfter=8,
        ),
        "question": ParagraphStyle(
            "Question",
            parent=base["BodyText"],
            fontName=SANS,
            fontSize=9.2,
            leading=13,
            textColor=INK,
            leftIndent=16,
            firstLineIndent=-12,
            spaceAfter=5,
        ),
        "table_head": ParagraphStyle(
            "TableHead",
            parent=base["BodyText"],
            fontName=SANS_BOLD,
            fontSize=8.4,
            leading=10.5,
            textColor=WHITE,
            alignment=TA_LEFT,
        ),
        "table": ParagraphStyle(
            "TableBody",
            parent=base["BodyText"],
            fontName=SANS,
            fontSize=8.1,
            leading=10.5,
            textColor=INK,
        ),
    }


def code(text: str, style_map: dict[str, ParagraphStyle]) -> Paragraph:
    return Paragraph("<br/>".join(escape(line) or " " for line in text.splitlines()), style_map["code"])


def bullet(text: str, style_map: dict[str, ParagraphStyle]) -> Paragraph:
    return Paragraph(f"- &nbsp; {text}", style_map["bullet"])


def table(
    rows: list[list[str]],
    widths: list[float],
    style_map: dict[str, ParagraphStyle],
    header: bool = True,
) -> Table:
    rendered = []
    for row_index, row in enumerate(rows):
        row_style = style_map["table_head"] if header and row_index == 0 else style_map["table"]
        rendered.append([Paragraph(value, row_style) for value in row])
    result = Table(rendered, colWidths=widths, repeatRows=1 if header else 0, hAlign="LEFT")
    commands = [
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("GRID", (0, 0), (-1, -1), 0.45, LINE),
    ]
    if header:
        commands.extend(
            [
                ("BACKGROUND", (0, 0), (-1, 0), NAVY),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, colors.HexColor("#F6F9FB")]),
            ]
        )
    result.setStyle(TableStyle(commands))
    return result


def arrow(drawing: Drawing, x1: float, y: float, x2: float, color=BLUE) -> None:
    drawing.add(Line(x1, y, x2 - 6, y, strokeColor=color, strokeWidth=1.4))
    drawing.add(
        Polygon(
            points=[x2 - 6, y + 3.5, x2, y, x2 - 6, y - 3.5],
            fillColor=color,
            strokeColor=color,
        )
    )


def pipeline_diagram() -> Drawing:
    drawing = Drawing(480, 112)
    boxes = [
        (5, "User text", "str", PALE_GREEN, GREEN),
        (102, "encode", "UTF-8", PALE_BLUE, BLUE),
        (199, "TCP stream", "bytes", PALE_ORANGE, ORANGE),
        (296, "frame buffer", "bytes", PALE_TEAL, TEAL),
        (393, "decode", "str", PALE_GREEN, GREEN),
    ]
    for x, label, detail, fill, stroke in boxes:
        drawing.add(Rect(x, 41, 82, 44, rx=5, ry=5, fillColor=fill, strokeColor=stroke, strokeWidth=1))
        drawing.add(String(x + 41, 66, label, textAnchor="middle", fontName=SANS_BOLD, fontSize=9, fillColor=INK))
        drawing.add(String(x + 41, 52, detail, textAnchor="middle", fontName=MONO, fontSize=8, fillColor=MUTED))
    for start in (87, 184, 281, 378):
        arrow(drawing, start + 2, 63, start + 14)
    drawing.add(String(240, 17, "Keep transport data as bytes; decode only complete frames.", textAnchor="middle", fontName=SANS, fontSize=9, fillColor=NAVY))
    return drawing


def chunk_diagram() -> Drawing:
    drawing = Drawing(480, 170)
    drawing.add(String(5, 153, "Application writes", fontName=SANS_BOLD, fontSize=9, fillColor=NAVY))
    app = [(118, 137, 78, "one\\n"), (200, 137, 78, "two\\n")]
    for x, y, width, label in app:
        drawing.add(Rect(x, y, width, 24, fillColor=PALE_GREEN, strokeColor=GREEN))
        drawing.add(String(x + width / 2, y + 8, label, textAnchor="middle", fontName=MONO, fontSize=9, fillColor=INK))
    drawing.add(String(5, 104, "Possible recv result A", fontName=SANS_BOLD, fontSize=9, fillColor=NAVY))
    drawing.add(Rect(118, 89, 160, 24, fillColor=PALE_BLUE, strokeColor=BLUE))
    drawing.add(String(198, 97, "one\\ntwo\\n", textAnchor="middle", fontName=MONO, fontSize=9, fillColor=INK))
    drawing.add(String(5, 56, "Possible recv result B", fontName=SANS_BOLD, fontSize=9, fillColor=NAVY))
    pieces = [(118, 41, 51, "on"), (173, 41, 73, "e\\ntw"), (250, 41, 28, "o\\n")]
    for x, y, width, label in pieces:
        drawing.add(Rect(x, y, width, 24, fillColor=PALE_ORANGE, strokeColor=ORANGE))
        drawing.add(String(x + width / 2, y + 8, label, textAnchor="middle", fontName=MONO, fontSize=8.5, fillColor=INK))
    drawing.add(String(240, 15, "TCP preserves byte order, not write or message boundaries.", textAnchor="middle", fontName=SANS_BOLD, fontSize=9.5, fillColor=RED))
    return drawing


def ownership_diagram() -> Drawing:
    drawing = Drawing(480, 176)
    drawing.add(Rect(160, 137, 160, 31, rx=5, ry=5, fillColor=PALE_BLUE, strokeColor=BLUE))
    drawing.add(String(240, 150, "Main thread: listening socket", textAnchor="middle", fontName=SANS_BOLD, fontSize=9.5, fillColor=INK))
    workers = [
        (20, "Worker A", "socket A", "buffer A"),
        (180, "Worker B", "socket B", "buffer B"),
        (340, "Worker C", "socket C", "buffer C"),
    ]
    for x, worker, sock, buff in workers:
        drawing.add(Line(240, 137, x + 60, 108, strokeColor=LINE, strokeWidth=1.2))
        drawing.add(Rect(x, 59, 120, 49, rx=5, ry=5, fillColor=PALE_TEAL, strokeColor=TEAL))
        drawing.add(String(x + 60, 91, worker, textAnchor="middle", fontName=SANS_BOLD, fontSize=9, fillColor=INK))
        drawing.add(String(x + 60, 77, sock, textAnchor="middle", fontName=MONO, fontSize=8, fillColor=MUTED))
        drawing.add(String(x + 60, 64, buff, textAnchor="middle", fontName=MONO, fontSize=8, fillColor=MUTED))
    drawing.add(String(240, 30, "Each connection has an independent ordered byte stream and independent incomplete state.", textAnchor="middle", fontName=SANS, fontSize=8.6, fillColor=NAVY))
    return drawing


def draw_page(canvas, document) -> None:
    canvas.saveState()
    width, height = A4
    if document.page > 1:
        canvas.setFont(SANS, 7.5)
        canvas.setFillColor(MUTED)
        canvas.drawString(19 * mm, height - 11 * mm, "Python Bytes and TCP Message Framing")
        canvas.setStrokeColor(LINE)
        canvas.line(19 * mm, height - 13 * mm, width - 19 * mm, height - 13 * mm)
    canvas.setStrokeColor(LINE)
    canvas.line(19 * mm, 14 * mm, width - 19 * mm, 14 * mm)
    canvas.setFont(SANS, 7.5)
    canvas.setFillColor(MUTED)
    canvas.drawString(19 * mm, 9 * mm, "TCP Chat Learning Project")
    canvas.drawRightString(width - 19 * mm, 9 * mm, f"Page {document.page}")
    canvas.restoreState()


def build_story(style_map: dict[str, ParagraphStyle]) -> list:
    s = style_map
    story: list = []

    # Cover
    story.extend(
        [
            Spacer(1, 34 * mm),
            Paragraph("Python Bytes and TCP Message Framing", s["title"]),
            Paragraph(
                "A step-by-step lesson for the threaded ephemeral chat server",
                s["subtitle"],
            ),
            Spacer(1, 8 * mm),
            pipeline_diagram(),
            Spacer(1, 12 * mm),
            Paragraph(
                "Core outcome: receive arbitrary TCP chunks, preserve incomplete bytes, "
                "produce complete newline-delimited messages, and keep memory bounded.",
                s["callout"],
            ),
            Spacer(1, 13 * mm),
            Paragraph("Lesson 3 - TCP Chat Learning Project", s["subtitle"]),
            PageBreak(),
        ]
    )

    # Page 2
    story.extend(
        [
            Paragraph("1. What you will learn", s["section"]),
            Paragraph(
                "This lesson connects Python's data types to the behavior of a real TCP connection. "
                "It focuses on the boundary between user text, transport bytes, and application messages.",
                s["body"],
            ),
            bullet("Distinguish <font name='LessonMono'>str</font>, <font name='LessonMono'>bytes</font>, and <font name='LessonMono'>bytearray</font>.", s),
            bullet("Encode text before sending and decode only after a complete frame is available.", s),
            bullet("Explain why <font name='LessonMono'>recv(1024)</font> returns up to 1,024 bytes, not one message.", s),
            bullet("Reassemble split messages and separate combined messages.", s),
            bullet("Give every client worker its own receive buffer.", s),
            bullet("Enforce a maximum frame size and decide what EOF means for incomplete data.", s),
            Paragraph("Learning path", s["h2"]),
            table(
                [
                    ["Step", "Question", "Evidence"],
                    ["1. Represent", "What are bytes?", "Inspect types, lengths, indexes, and encoded values."],
                    ["2. Transport", "What does TCP deliver?", "Predict multiple valid recv chunkings."],
                    ["3. Frame", "Where does a message end?", "Extract newline-delimited frames."],
                    ["4. Bound", "What can go wrong?", "Reject oversized and malformed frames."],
                    ["5. Test", "Can it survive arbitrary chunks?", "Pass deterministic unit tests without sockets."],
                ],
                [24 * mm, 52 * mm, 90 * mm],
                s,
            ),
            Spacer(1, 7),
            Paragraph(
                "Definition of done: your framing code returns the same complete messages regardless of how the same byte stream is divided across recv calls.",
                s["callout"],
            ),
            PageBreak(),
        ]
    )

    # Page 3
    story.extend(
        [
            Paragraph("2. Python text and bytes", s["section"]),
            Paragraph(
                "Python text is Unicode. A socket carries bytes. Encoding and decoding form the explicit boundary between those two representations.",
                s["body"],
            ),
            code(
                'text = "café"                 # str\n'
                'wire = text.encode("utf-8")   # bytes\n\n'
                'print(type(text))              # <class \'str\'>\n'
                'print(wire)                    # b\'caf\\xc3\\xa9\'\n'
                'print(len(text))               # 4 characters\n'
                'print(len(wire))               # 5 bytes\n'
                'print(wire.decode("utf-8"))    # café',
                s,
            ),
            Paragraph("Indexing behaves differently", s["h2"]),
            code(
                'data = b"ABC"\n'
                'data[0]      # 65: indexing returns an integer\n'
                'data[0:1]    # b\'A\': slicing returns bytes\n'
                'list(data)   # [65, 66, 67]',
                s,
            ),
            Paragraph("Operations you will use", s["h2"]),
            table(
                [
                    ["Expression", "Result", "Meaning"],
                    ["<font name='LessonMono'>b'\\n' in data</font>", "Boolean", "A complete delimiter has arrived."],
                    ["<font name='LessonMono'>left + right</font>", "New bytes", "Combine saved and newly received bytes."],
                    ["<font name='LessonMono'>data.split(b'\\n', 1)</font>", "Two byte parts", "Extract the first complete frame."],
                    ["<font name='LessonMono'>data.decode('utf-8')</font>", "Text", "Interpret a complete byte frame as text."],
                    ["<font name='LessonMono'>repr(data)</font>", "Debug text", "Make newlines and escaped bytes visible."],
                ],
                [53 * mm, 31 * mm, 82 * mm],
                s,
            ),
            Paragraph(
                "Do not mix the types accidentally: <font name='LessonMono'>\"hello\" + b\"world\"</font> raises <font name='LessonMono'>TypeError</font>.",
                s["callout"],
            ),
            PageBreak(),
        ]
    )

    # Page 4
    story.extend(
        [
            Paragraph("3. The socket boundary", s["section"]),
            pipeline_diagram(),
            Paragraph("Sending", s["h2"]),
            code(
                'message_text = input("> ")\n'
                'wire_frame = (message_text + "\\n").encode("utf-8")\n'
                'client.sendall(wire_frame)',
                s,
            ),
            Paragraph(
                "The newline is part of the application protocol. <font name='LessonMono'>sendall()</font> hands the full encoded frame toward the operating system or raises an error. It does not confirm that another person read the message.",
                s["body"],
            ),
            Paragraph("Receiving", s["h2"]),
            code(
                'chunk = connection.recv(BUFFER_SIZE)\n\n'
                'if chunk == b"":\n'
                '    # The peer closed its sending side.\n'
                '    break',
                s,
            ),
            table(
                [
                    ["Value returned by recv", "Interpretation"],
                    ["<font name='LessonMono'>b'hello\\n'</font>", "Some bytes are available. They may contain part, one, or several frames."],
                    ["<font name='LessonMono'>b'h'</font>", "Only one byte was available even if a larger recv size was requested."],
                    ["<font name='LessonMono'>b''</font>", "EOF: the peer closed its sending side. No more bytes will arrive."],
                ],
                [58 * mm, 108 * mm],
                s,
            ),
            Paragraph(
                "An empty chat frame is <font name='LessonMono'>b'\\n'</font>. A zero-byte result <font name='LessonMono'>b''</font> is connection state, not a message.",
                s["callout"],
            ),
            PageBreak(),
        ]
    )

    # Page 5
    story.extend(
        [
            Paragraph("4. Why recv cannot define messages", s["section"]),
            chunk_diagram(),
            Paragraph(
                "The application may call <font name='LessonMono'>sendall()</font> once per message, but TCP exposes one ordered stream. The receiver chooses how much currently available data to return, capped by the recv argument.",
                s["body"],
            ),
            table(
                [
                    ["Client action", "Valid server observations"],
                    ["<font name='LessonMono'>sendall(b'hello\\n')</font>", "<font name='LessonMono'>b'hello\\n'</font> or <font name='LessonMono'>b'he'</font> then <font name='LessonMono'>b'llo\\n'</font>"],
                    ["Send <font name='LessonMono'>one\\n</font>, then <font name='LessonMono'>two\\n</font>", "One combined chunk, two chunks, or several smaller chunks"],
                    ["Send 5,000 bytes; call <font name='LessonMono'>recv(1024)</font>", "At least five positive receives are required, possibly more"],
                ],
                [70 * mm, 96 * mm],
                s,
            ),
            Paragraph("Two separate limits", s["h2"]),
            bullet("<b>Chunk size</b>: how many bytes one <font name='LessonMono'>recv()</font> call may return. It is an implementation choice, not a protocol rule.", s),
            bullet("<b>Frame size</b>: the largest message your protocol accepts. It is a protocol and resource-safety rule.", s),
            Paragraph(
                "Changing <font name='LessonMono'>BUFFER_SIZE</font> changes chunking behavior and call frequency. It does not remove the need for framing.",
                s["callout"],
            ),
            PageBreak(),
        ]
    )

    # Page 6
    story.extend(
        [
            Paragraph("5. The framing buffer, step by step", s["section"]),
            Paragraph(
                "The buffer contains bytes received for one connection that have not yet been emitted as complete frames.",
                s["body"],
            ),
            table(
                [
                    ["Event", "Received chunk", "Buffer after append", "Frames emitted", "Remainder"],
                    ["1", "<font name='LessonMono'>b'hel'</font>", "<font name='LessonMono'>b'hel'</font>", "None", "<font name='LessonMono'>b'hel'</font>"],
                    ["2", "<font name='LessonMono'>b'lo\\nwor'</font>", "<font name='LessonMono'>b'hello\\nwor'</font>", "<font name='LessonMono'>b'hello'</font>", "<font name='LessonMono'>b'wor'</font>"],
                    ["3", "<font name='LessonMono'>b'ld\\nnext\\n'</font>", "<font name='LessonMono'>b'world\\nnext\\n'</font>", "<font name='LessonMono'>b'world'</font>, <font name='LessonMono'>b'next'</font>", "<font name='LessonMono'>b''</font>"],
                ],
                [14 * mm, 35 * mm, 48 * mm, 43 * mm, 31 * mm],
                s,
            ),
            Paragraph("Algorithm", s["h2"]),
            code(
                'buffer = b""\n\n'
                'repeat:\n'
                '    chunk = recv(up_to_BUFFER_SIZE_bytes)\n'
                '    if chunk is EOF:\n'
                '        apply the incomplete-frame policy and stop\n\n'
                '    buffer = buffer + chunk\n\n'
                '    while buffer contains b"\\n":\n'
                '        remove one complete byte frame\n'
                '        decode that frame as UTF-8\n'
                '        handle the resulting message\n\n'
                '    enforce the maximum unfinished-frame size',
                s,
            ),
            Paragraph("Why the inner loop matters", s["h2"]),
            Paragraph(
                "A single chunk can contain <font name='LessonMono'>b'one\\ntwo\\nthree\\n'</font>. Using <font name='LessonMono'>if</font> would process only one frame and leave two complete frames waiting until some future network activity. Using <font name='LessonMono'>while</font> drains every complete frame already available.",
                s["body"],
            ),
            Paragraph(
                "Invariant after processing: the remainder contains no newline and is the exact prefix of the next possible frame.",
                s["callout"],
            ),
            PageBreak(),
        ]
    )

    # Page 7
    story.extend(
        [
            Paragraph("6. Unicode and decode timing", s["section"]),
            Paragraph(
                "UTF-8 characters may contain more than one byte. TCP can divide the stream between those bytes, so decoding arbitrary recv chunks can reject valid text.",
                s["body"],
            ),
            code(
                'wire = "café\\n".encode("utf-8")\n'
                '# b\'caf\\xc3\\xa9\\n\'\n\n'
                '# A possible split:\n'
                'chunk_1 = b"caf\\xc3"\n'
                'chunk_2 = b"\\xa9\\n"\n\n'
                'chunk_1.decode("utf-8")\n'
                '# UnicodeDecodeError: the final character is incomplete',
                s,
            ),
            Paragraph("Safe sequence", s["h2"]),
            table(
                [
                    ["Stage", "Representation", "Action"],
                    ["Receive", "Arbitrary bytes", "Append chunks without decoding."],
                    ["Frame", "Complete byte frame", "Remove the delimiter and enforce the byte limit."],
                    ["Decode", "Complete UTF-8 sequence", "Use strict UTF-8; reject malformed frames."],
                    ["Validate", "Python text", "Check empty text, commands, usernames, and content rules."],
                ],
                [31 * mm, 50 * mm, 85 * mm],
                s,
            ),
            Paragraph("Protocol decisions", s["h2"]),
            bullet("Will an empty frame <font name='LessonMono'>b'\\n'</font> be accepted or ignored?", s),
            bullet("Can message text contain line breaks? If yes, newline framing needs escaping or replacement.", s),
            bullet("What happens after invalid UTF-8: error response, dropped frame, or disconnected client?", s),
            bullet("Is the maximum measured in encoded bytes or decoded characters? Use encoded bytes for transport safety.", s),
            Paragraph(
                "For this chat: one terminal input line becomes one UTF-8 frame; embedded newlines are not allowed; malformed UTF-8 is a protocol error.",
                s["callout"],
            ),
            PageBreak(),
        ]
    )

    # Page 8
    story.extend(
        [
            Paragraph("7. Requirements and failure policies", s["section"]),
            table(
                [
                    ["Requirement", "Why it exists", "Recommended policy"],
                    ["Delimiter", "TCP supplies no message boundary.", "Every frame ends in one <font name='LessonMono'>b'\\n'</font>."],
                    ["Maximum frame", "A client can send forever without a delimiter.", "Reject when unfinished data exceeds 4,096 bytes."],
                    ["Encoding", "Peers must interpret bytes consistently.", "UTF-8 with strict decoding."],
                    ["EOF policy", "A client may close during a frame.", "Discard the unfinished remainder and record metadata only."],
                    ["Empty frame", "<font name='LessonMono'>b'\\n'</font> is a valid frame structurally.", "Ignore or reject it explicitly."],
                    ["Malformed UTF-8", "Bad data must not crash a worker.", "Send a protocol error or disconnect that client."],
                    ["Ephemeral content", "The product promises no history.", "Never write message content to files or logs."],
                ],
                [35 * mm, 65 * mm, 66 * mm],
                s,
            ),
            Paragraph("Important invariants", s["h2"]),
            bullet("Frames are emitted exactly once and in byte-stream order.", s),
            bullet("After extraction, the remainder contains no complete delimiter.", s),
            bullet("A worker never reads from another client's buffer or socket.", s),
            bullet("Routing receives complete decoded messages, never raw chunks.", s),
            bullet("No incomplete frame can grow beyond the configured limit.", s),
            Paragraph("Ephemeral does not mean zero memory", s["h2"]),
            Paragraph(
                "Bytes must exist transiently in kernel buffers and application memory while being received, framed, and relayed. The guarantee is that content is not persisted, retained as history, or included in logs. Keep temporary references short-lived and bounded.",
                s["body"],
            ),
            Paragraph(
                "A requirement becomes useful when it specifies observable behavior for success, malformed input, EOF, and resource exhaustion.",
                s["callout"],
            ),
            PageBreak(),
        ]
    )

    # Page 9
    story.extend(
        [
            Paragraph("8. Ownership in the threaded server", s["section"]),
            ownership_diagram(),
            Paragraph(
                "The main thread owns the listening socket. After <font name='LessonMono'>accept()</font>, one worker owns the connected socket and its incomplete-frame state. A framing helper may be shared as code, but its state must remain per connection.",
                s["body"],
            ),
            Paragraph("A testable module boundary", s["h2"]),
            code(
                '# framing.py\n'
                'def extract_frames(\n'
                '    existing_buffer: bytes,\n'
                '    received_chunk: bytes,\n'
                ') -> tuple[list[bytes], bytes]:\n'
                '    """Return complete frames and unfinished bytes."""\n'
                '    ...',
                s,
            ),
            code(
                '# server.py\n'
                'from framing import extract_frames\n\n'
                'buffer = b""\n'
                'chunk = connection.recv(BUFFER_SIZE)\n'
                'frames, buffer = extract_frames(buffer, chunk)',
                s,
            ),
            Paragraph("Why this separation is valuable", s["h2"]),
            bullet("Framing tests do not need ports, timing, threads, or live sockets.", s),
            bullet("The server coordinates I/O; the framing module interprets byte structure.", s),
            bullet("A future length-prefixed framer can replace the delimiter framer without rewriting socket ownership.", s),
            Paragraph(
                "Start with a pure function so state movement is visible. A <font name='LessonMono'>LineFramer</font> class is appropriate later if it improves the interface rather than hiding the lesson.",
                s["callout"],
            ),
            PageBreak(),
        ]
    )

    # Page 10
    story.extend(
        [
            Paragraph("9. Deterministic framing tests", s["section"]),
            Paragraph(
                "The same logical stream should produce the same frames for every chunk division. These tests model TCP behavior without relying on nondeterministic network timing.",
                s["body"],
            ),
            table(
                [
                    ["Existing", "Incoming", "Expected frames", "Expected remainder"],
                    ["<font name='LessonMono'>b''</font>", "<font name='LessonMono'>b'hello\\n'</font>", "<font name='LessonMono'>[b'hello']</font>", "<font name='LessonMono'>b''</font>"],
                    ["<font name='LessonMono'>b''</font>", "<font name='LessonMono'>b'hel'</font>", "<font name='LessonMono'>[]</font>", "<font name='LessonMono'>b'hel'</font>"],
                    ["<font name='LessonMono'>b'hel'</font>", "<font name='LessonMono'>b'lo\\n'</font>", "<font name='LessonMono'>[b'hello']</font>", "<font name='LessonMono'>b''</font>"],
                    ["<font name='LessonMono'>b''</font>", "<font name='LessonMono'>b'one\\ntwo\\n'</font>", "<font name='LessonMono'>[b'one', b'two']</font>", "<font name='LessonMono'>b''</font>"],
                    ["<font name='LessonMono'>b''</font>", "<font name='LessonMono'>b'one\\ntw'</font>", "<font name='LessonMono'>[b'one']</font>", "<font name='LessonMono'>b'tw'</font>"],
                    ["<font name='LessonMono'>b''</font>", "<font name='LessonMono'>b'\\n'</font>", "<font name='LessonMono'>[b'']</font>", "<font name='LessonMono'>b''</font>"],
                ],
                [32 * mm, 45 * mm, 51 * mm, 43 * mm],
                s,
            ),
            Paragraph("Property to reason about", s["h2"]),
            code(
                'stream = b"one\\ntwo\\npartial"\n\n'
                '# These chunk sequences describe the same stream:\n'
                '[stream]\n'
                '[b"o", b"ne\\ntwo\\npartial"]\n'
                '[b"one\\n", b"two\\n", b"partial"]\n\n'
                '# Every sequence must finish with:\n'
                'frames == [b"one", b"two"]\n'
                'remainder == b"partial"',
                s,
            ),
            Paragraph("Add negative tests", s["h2"]),
            bullet("Unfinished data exceeds the maximum frame size.", s),
            bullet("A frame is exactly at the size limit.", s),
            bullet("A complete frame contains malformed UTF-8.", s),
            bullet("EOF arrives while the remainder is non-empty.", s),
            Paragraph(
                "Unit tests should control chunk boundaries deliberately. Integration tests should verify that the framing module is wired into the real worker correctly.",
                s["callout"],
            ),
            PageBreak(),
        ]
    )

    # Page 11
    story.extend(
        [
            Paragraph("10. Hands-on lesson", s["section"]),
            Paragraph("Part A - Explore bytes in the Python shell", s["h2"]),
            code(
                'text = "café"\n'
                'wire = text.encode("utf-8")\n'
                'type(text), type(wire)\n'
                'len(text), len(wire)\n'
                'list(wire)\n'
                'wire[0], wire[0:1]\n'
                'wire.decode("utf-8")',
                s,
            ),
            Paragraph("Before pressing Enter, predict every result. Explain why character count and byte count differ.", s["small"]),
            Paragraph("Part B - Manually reconstruct a frame", s["h2"]),
            code(
                'buffer = b""\n'
                'buffer += b"hel"\n'
                'b"\\n" in buffer\n'
                'buffer += b"lo\\nnext"\n'
                'message, buffer = buffer.split(b"\\n", 1)\n'
                'message, buffer, message.decode("utf-8")',
                s,
            ),
            Paragraph("Expected final state: <font name='LessonMono'>message == b'hello'</font> and <font name='LessonMono'>buffer == b'next'</font>.", s["small"]),
            Paragraph("Part C - Implement the framing contract", s["h2"]),
            bullet("Create <font name='LessonMono'>framing.py</font> beside <font name='LessonMono'>server.py</font>.", s),
            bullet("Implement <font name='LessonMono'>extract_frames(existing_buffer, received_chunk)</font>.", s),
            bullet("Keep the function concerned with bytes; decode in the protocol or server layer.", s),
            bullet("Write the deterministic tests from the previous page.", s),
            bullet("Run <font name='LessonMono'>python -m unittest -v test_framing.py</font>.", s),
            Paragraph("Part D - Integrate only after unit tests pass", s["h2"]),
            bullet("Create one buffer inside each <font name='LessonMono'>handle_client()</font> call.", s),
            bullet("Feed every positive recv chunk to the framing function.", s),
            bullet("Decode and temporarily display every returned complete frame.", s),
            bullet("Apply the EOF and maximum-size policies.", s),
            PageBreak(),
        ]
    )

    # Page 12
    story.extend(
        [
            Paragraph("11. Assessment and review", s["section"]),
            Paragraph("Explain without looking", s["h2"]),
            Paragraph("1. &nbsp; Why can a six-byte message require several <font name='LessonMono'>recv(1024)</font> calls?", s["question"]),
            Paragraph("2. &nbsp; Why can two <font name='LessonMono'>sendall()</font> calls appear in one recv chunk?", s["question"]),
            Paragraph("3. &nbsp; What is the difference between chunk size and maximum frame size?", s["question"]),
            Paragraph("4. &nbsp; Why does every worker need a separate buffer?", s["question"]),
            Paragraph("5. &nbsp; Why should UTF-8 decoding happen after framing?", s["question"]),
            Paragraph("6. &nbsp; What does <font name='LessonMono'>b''</font> from <font name='LessonMono'>recv()</font> mean?", s["question"]),
            Paragraph("7. &nbsp; How does a size limit prevent a memory-exhaustion bug?", s["question"]),
            Paragraph("8. &nbsp; Why does transient buffering still fit an ephemeral-chat requirement?", s["question"]),
            Paragraph("Practical evidence", s["h2"]),
            bullet("All deterministic framing tests pass.", s),
            bullet("One frame split over multiple inputs is emitted once and only when complete.", s),
            bullet("Several frames in one input are all emitted immediately and in order.", s),
            bullet("Unicode text survives arbitrary byte chunking.", s),
            bullet("Oversized unfinished input is rejected without unbounded growth.", s),
            bullet("Three connected clients keep independent remainder buffers.", s),
            Paragraph("Official reading", s["h2"]),
            Paragraph(
                '<link href="https://docs.python.org/3/howto/sockets.html" color="#2574A9">Python Socket Programming HOWTO</link> - read the sections on send, recv, and message framing.',
                s["body"],
            ),
            Paragraph(
                '<link href="https://docs.python.org/3/library/socket.html" color="#2574A9">Python socket reference</link> - use for exact operation contracts.',
                s["body"],
            ),
            Paragraph(
                '<link href="https://docs.python.org/3/library/asyncio-stream.html" color="#2574A9">Python asyncio streams</link> - compare readuntil, readexactly, and configured limits.',
                s["body"],
            ),
            Paragraph(
                '<link href="https://www.rfc-editor.org/rfc/rfc9293.html" color="#2574A9">RFC 9293</link> - the formal TCP byte-stream specification.',
                s["body"],
            ),
            Paragraph(
                "Next milestone: complete the framing module before adding message broadcasting or disappearing-message timers.",
                s["callout"],
            ),
        ]
    )
    return story


def build() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    style_map = styles()
    document = SimpleDocTemplate(
        str(OUTPUT),
        pagesize=A4,
        leftMargin=19 * mm,
        rightMargin=19 * mm,
        topMargin=18 * mm,
        bottomMargin=19 * mm,
        title="Python Bytes and TCP Message Framing",
        author="TCP Chat Learning Project",
        subject="Byte handling, buffering, framing, and protocol requirements in Python TCP applications",
    )
    document.build(build_story(style_map), onFirstPage=draw_page, onLaterPages=draw_page)
    print(OUTPUT)


if __name__ == "__main__":
    build()

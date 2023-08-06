import math
import random
import unittest
from datetime import datetime
from pathlib import Path

from borb.io.read.types import Decimal
from borb.pdf.canvas.color.color import HexColor
from borb.pdf.canvas.geometry.rectangle import Rectangle
from borb.pdf.canvas.layout.layout_element import Alignment
from borb.pdf.canvas.layout.page_layout.multi_column_layout import SingleColumnLayout
from borb.pdf.canvas.layout.shape.disjoint_shape import DisjointShape
from borb.pdf.canvas.layout.table.fixed_column_width_table import (
    FixedColumnWidthTable as Table,
)
from borb.pdf.canvas.layout.text.paragraph import Paragraph
from borb.pdf.canvas.line_art.line_art_factory import LineArtFactory
from borb.pdf.document.document import Document
from borb.pdf.page.page import Page
from borb.pdf.pdf import PDF
from tests.test_util import compare_visually_to_ground_truth, check_pdf_using_validator


class TestWriteEurion(unittest.TestCase):
    """
    This test creates a PDF with an eurion symbol in it
    """

    def __init__(self, methodName="runTest"):
        super().__init__(methodName)
        # find output dir
        p: Path = Path(__file__).parent
        while "output" not in [x.stem for x in p.iterdir() if x.is_dir()]:
            p = p.parent
        p = p / "output"
        self.output_dir = Path(p, Path(__file__).stem.replace(".py", ""))
        if not self.output_dir.exists():
            self.output_dir.mkdir()

    def _write_eurion(
        self,
        page: Page,
        layout: SingleColumnLayout,
    ):
        w = page.get_page_info().get_width()
        h = page.get_page_info().get_height() - Decimal(200)
        assert w is not None
        assert h is not None
        layout.add(
            DisjointShape(
                LineArtFactory.EURion(Rectangle(0, 0, 50, 50)),
                horizontal_alignment=Alignment.CENTERED,
                vertical_alignment=Alignment.MIDDLE,
                stroke_color=HexColor("ff0000"),
                line_width=Decimal(3),
            ),
        )

    def _write_eurion_rotated(
        self,
        page: Page,
        layout: SingleColumnLayout,
    ):
        w = page.get_page_info().get_width()
        h = page.get_page_info().get_height() - Decimal(200)
        assert w is not None
        assert h is not None
        layout.add(
            DisjointShape(
                LineArtFactory.EURion(Rectangle(0, 0, 50, 50)),
                horizontal_alignment=Alignment.CENTERED,
                vertical_alignment=Alignment.MIDDLE,
                stroke_color=HexColor("ff0000"),
                line_width=Decimal(3),
            ).rotate(math.radians(45)),
        )

    def test_write_document_001(self):

        # create document
        pdf = Document()

        # add page
        page = Page()
        pdf.add_page(page)

        # add test information
        layout = SingleColumnLayout(page)
        layout.add(
            Table(number_of_columns=2, number_of_rows=3)
            .add(Paragraph("Date", font="Helvetica-Bold"))
            .add(Paragraph(datetime.now().strftime("%d/%m/%Y, %H:%M:%S")))
            .add(Paragraph("Test", font="Helvetica-Bold"))
            .add(Paragraph(Path(__file__).stem))
            .add(Paragraph("Description", font="Helvetica-Bold"))
            .add(Paragraph("This test creates a PDF with an EURion shape in it."))
            .set_padding_on_all_cells(Decimal(2), Decimal(2), Decimal(2), Decimal(2))
        )

        self._write_eurion(page, layout)

        # determine output location
        out_file = self.output_dir / "output_001.pdf"

        # attempt to store PDF
        with open(out_file, "wb") as in_file_handle:
            PDF.dumps(in_file_handle, pdf)

        with open(out_file, "rb") as in_file_handle:
            PDF.loads(in_file_handle)

        compare_visually_to_ground_truth(out_file)
        check_pdf_using_validator(out_file)

    def test_write_document_002(self):

        # create document
        pdf = Document()

        # add page
        page = Page()
        pdf.add_page(page)

        # add test information
        layout = SingleColumnLayout(page)
        layout.add(
            Table(number_of_columns=2, number_of_rows=3)
            .add(Paragraph("Date", font="Helvetica-Bold"))
            .add(Paragraph(datetime.now().strftime("%d/%m/%Y, %H:%M:%S")))
            .add(Paragraph("Test", font="Helvetica-Bold"))
            .add(Paragraph(Path(__file__).stem))
            .add(Paragraph("Description", font="Helvetica-Bold"))
            .add(Paragraph("This test creates a PDF with an EURion shape in it."))
            .set_padding_on_all_cells(Decimal(2), Decimal(2), Decimal(2), Decimal(2))
        )

        self._write_eurion_rotated(page, layout)

        # determine output location
        out_file = self.output_dir / "output_002.pdf"

        # attempt to store PDF
        with open(out_file, "wb") as in_file_handle:
            PDF.dumps(in_file_handle, pdf)

        with open(out_file, "rb") as in_file_handle:
            PDF.loads(in_file_handle)

        compare_visually_to_ground_truth(out_file)
        check_pdf_using_validator(out_file)

from typing import List
from io import BytesIO
from xlsxwriter import Workbook

from app.src.exceptions.report import NoDataForCreatingReport


class ReportGenerator:
    header_styles = {
        "bold": True,
        "bg_color": "#A6DBDD",
        "border": 1,
        "align": "center",
        "valign": "vcenter",
    }

    async def generate(self, data: List[dict], file: BytesIO):
        if not data:
            raise NoDataForCreatingReport

        headers = data[0].keys()

        workbook = Workbook(file, {"in_memory": True})
        worksheet = workbook.add_worksheet()

        header_format = workbook.add_format(self.header_styles)

        for col, header in enumerate(headers):
            worksheet.write(0, col, header, header_format)

        for row in range(len(data)):
            values = data[row].values()
            for col, value in enumerate(values):
                worksheet.write(row + 1, col, value)

        workbook.close()

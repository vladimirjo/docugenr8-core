import xml.etree.ElementTree as ET  # noqa: N817
from xml.etree.ElementTree import Element


class Svg:
    def __init__(self, path: str) -> None:
        self.root: Element = ET.parse("/mnt/c/dev/svg/example.svg").getroot()
        self.groups: dict[str, list[object]]
        self.elements: list[object]

    def build_elements(self) -> list[object]:
        elements: list[object] = []
        for element in self.root.items():
            print(element)
        return elements

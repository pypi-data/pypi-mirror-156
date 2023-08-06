from typing import List, Optional, Dict, Any

from pygsuite.common.style import TextStyle
from pygsuite.docs.doc_elements.paragraph import Paragraph
from pygsuite.docs.element import DocElement


class Body(object):
    def __init__(self, body, document):
        from pygsuite import Document

        self._document: Document = document
        self._pending = []

    @property
    def _body(self):
        return self._document._document.get("body")

    @property
    def content(self) -> List[DocElement]:
        content_len = len(self._body.get("content"))
        return [
            DocElement(element, self._document, idx == content_len - 1)
            for idx, element in enumerate(self._body.get("content"))
        ]

    @content.setter
    def content(self, x):
        self._body["content"] = x

    @property
    def paragraphs(self) -> List[Paragraph]:
        return [item for item in self.content if isinstance(item, Paragraph)]

    def delete(self, flush=True):
        # save the last character of the last element
        for object in reversed(self.content):
            object.delete()
        if flush:
            self._document.flush()
        self.content = []  # type: ignore

    @property
    def start_index(self):
        return self.content[0].start_index

    @property
    def end_index(self):
        return self.content[-1].end_index + sum(self._pending)

    @property
    def _end_index_append(self):
        if not self._pending and not self.content:
            return 1
        elif not self.content:
            return sum(self._pending)
        else:
            return self.content[-1].end_index + sum(self._pending)

    def __getitem__(self, item):
        return self.content[item]

    def __setitem__(self, index, value, style=None):
        self.content[index] = value

    def newline(self, count: int = 1):
        self.add_text("\n" * count)

    @property
    def text(self):

        return "".join([element.text for element in self.content if isinstance(element, Paragraph)])

    def flush(self):
        self._document.flush()

    def add_text(self, text: str, position: int = None, style: TextStyle = None):
        # TOOD: add warning
        position = 1 if position == 0 else position
        self._pending.append(len(text))
        if style and not position and self._document._change_queue:
            # if there are pending changes
            # we currently need to flush them to infer proper style positioning
            # TODO: calculate this virtually
            # We could get the size of each pending object, track it, and infer the appropriate style index
            # without flushing
            self._document.flush()
        message: Dict[str, Dict[str, Any]] = {"insertText": {"text": text}}
        if position is not None:
            message["insertText"]["location"] = {"index": position}
        else:
            message["insertText"]["endOfSegmentLocation"] = {}
        queued = [message]

        if style:
            start = position
            if start is None:
                if not self.content:
                    start = 1
                else:
                    start = self.content[-1].end_index - 1

            end = start + len(text)
            fields, style_dict = style.to_doc_style()
            queued.append(
                {
                    "updateTextStyle": {
                        "range": {"startIndex": start, "endIndex": end},
                        "textStyle": style_dict,
                        "fields": fields,
                    }
                }
            )

        self._document._mutation(queued)

    def add_image(
        self, uri, position: Optional[int] = None, height: Optional[int] = None, width=Optional[int]
    ):
        """Add an image to the document at the specified location."""
        message = {
            "insertInlineImage": {
                "uri": uri,
                # "objectSize": {
                #     object (Size)
                # }
            }
        }
        if height or width:
            size = {}
            if height:
                size["height"] = height
            if width:
                size["width"] = width
            message["insertInlineImage"]["objectSize"] = size
        if position:
            message["insertInlineImage"]["location"] = {"index": position}
        else:
            message["insertInlineImage"]["endOfSegmentLocation"] = {}
        self._document._mutation([message])

    def style(self, style: TextStyle, start: int, end: int):
        # TODO: finish this method
        fields, style_dict = style.to_doc_style()
        message = {
            "updateTextStyle": {
                "textStyle": style_dict,
                "range": {"startIndex": start, "endIndex": end},
                "fields": fields,
            }
        }
        return message

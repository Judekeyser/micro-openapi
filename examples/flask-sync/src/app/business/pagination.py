from typing import Optional

from pydantic import BaseModel


class Paginated(BaseModel):
    page_size: int
    page: int = 1

    @property
    def is_valid(self) -> bool:
        return self.page_size > 0 and self.page > 0

    @property
    def start(self) -> int:
        return (self.page - 1) * self.page_size

    @property
    def stop(self) -> int:
        return self.start + self.page_size

    def previous(self, total_count: Optional[int]=None) -> Optional['Paginated']:
        if self.page > 1:
            if total_count is None:
                previous_page = self.page - 1
            else:
                if total_count == 0:
                    previous_page = 1
                else:
                    last_page = (total_count + self.page_size - 1) // self.page_size
                    previous_page = min(last_page, self.page - 1)

            return Paginated(
                page=previous_page,
                page_size=self.page_size
            )
        return None

    def next(self, total_count: Optional[int]) -> Optional['Paginated']:
        total_so_far = self.page * self.page_size
        if (total_count is None) or (total_count > total_so_far):
            return Paginated(
                page=self.page + 1,
                page_size=self.page_size
            )
        return None


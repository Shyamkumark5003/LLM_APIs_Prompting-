from pydantic import BaseModel, Field


class Experience(BaseModel):
    company: str
    title: str
    years: float | None = None


class CVData(BaseModel):
    name: str
    email: str | None = None
    phone: str | None = None
    location: str | None = None
    skills: list[str] = Field(default_factory=list)
    experience: list[Experience] = Field(default_factory=list)
    education: str | None = None
    total_years_experience: float | None = None


class LineItem(BaseModel):
    description: str
    quantity: float | None = None
    amount: float | None = None


class InvoiceData(BaseModel):
    vendor: str | None = None
    invoice_number: str | None = None
    invoice_date: str | None = None
    bill_to: str | None = None
    currency: str | None = None
    total: float | None = None
    line_items: list[LineItem] = Field(default_factory=list)

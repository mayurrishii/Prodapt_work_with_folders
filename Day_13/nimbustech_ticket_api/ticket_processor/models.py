class Tickets:
    def __init__(self,ticket_id,customer_name,category,priority,created_at,sla_hours,status):
        self.ticket_id = ticket_id
        self.customer_name = customer_name
        self.category = category
        self.priority = priority
        self.created_at = created_at
        self.sla_hours = sla_hours
        self.status = status
    def __str__(self):
        return f"Tickets(ticket_id={self.ticket_id}, customer_name={self.customer_name}, category={self.category}, priority={self.priority}, created_at={self.created_at}, sla_hours={self.sla_hours}, status={self.status})"

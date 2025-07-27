#!/usr/bin/env python3
"""
Comprehensive end-to-end simulation of the AdCP:Buy lifecycle.
Demonstrates the full workflow from planning through campaign completion.
"""

import asyncio
from datetime import date, timedelta
from typing import Dict, List, Optional
from fastmcp.client import Client
from fastmcp.client.transports import StreamableHttpTransport
from rich.console import Console
from rich.rule import Rule
from rich.table import Table
from rich.panel import Panel
from rich.progress import track
import time

from schemas import *

console = Console()

# Principal tokens
PURINA_TOKEN = "purina_secret_token_abc123"
ACME_TOKEN = "acme_secret_token_xyz789"

class FullLifecycleSimulation:
    """Complete AdCP:Buy lifecycle simulation with time progression."""
    
    def __init__(self, server_url: str, token: str, principal_id: str):
        headers = {"x-adcp-auth": token}
        transport = StreamableHttpTransport(url=f"{server_url}/mcp/", headers=headers)
        self.client = Client(transport=transport)
        self.principal_id = principal_id
        self.media_buy_id: Optional[str] = None
        self.creative_ids: List[str] = []
        self.products: List[Dict] = []
        
        # Timeline setup - campaign in August 2025
        self.planning_date = date(2025, 6, 5)  # Early June - planning phase
        self.buy_date = date(2025, 6, 15)      # Mid June - make the buy
        self.creative_date = date(2025, 6, 20) # Late June - submit creatives
        self.flight_start = date(2025, 8, 1)   # August 1 - campaign starts
        self.flight_end = date(2025, 8, 15)    # August 15 - campaign ends
        
    async def run(self):
        """Run the complete simulation."""
        console.print(Rule(f"[bold magenta]AdCP:Buy Full Lifecycle Simulation[/bold magenta]", style="magenta"))
        console.print(f"[cyan]Principal: {self.principal_id}[/cyan]")
        console.print(f"[cyan]Campaign Period: {self.flight_start} to {self.flight_end}[/cyan]\n")
        
        async with self.client:
            await self._phase_1_planning()
            await self._phase_2_buying()
            await self._phase_3_creatives()
            await self._phase_4_pre_flight()
            await self._phase_5_in_flight()
            await self._phase_6_optimization()
            await self._phase_7_completion()
            
            # Dry run logs are now shown by adapters during execution
            # await self._show_dry_run_logs()
    
    async def _call_tool(self, tool_name: str, params: dict = {}) -> Dict:
        """Call a tool and return structured content."""
        try:
            result = await self.client.call_tool(tool_name, params)
            return result.structured_content if hasattr(result, 'structured_content') else {}
        except Exception as e:
            console.print(f"[red]Error calling {tool_name}: {e}[/red]")
            return {}
    
    def _show_day(self, current_date: date, activity: str):
        """Display current simulation day and activity."""
        console.print(f"\n[bold blue]📅 {current_date.strftime('%B %d, %Y')}[/bold blue] - {activity}")
        time.sleep(0.5)  # Small delay for visual effect
    
    async def _phase_1_planning(self):
        """Phase 1: Planning - Review available products."""
        console.print(Rule("[bold cyan]Phase 1: Planning & Discovery[/bold cyan]", style="cyan"))
        
        self._show_day(self.planning_date, "Beginning campaign planning")
        
        # List available products
        console.print("\n[yellow]Discovering available media products...[/yellow]")
        products_response = await self._call_tool("list_products", {"req": {"brief": "Looking for video and audio inventory for pet food campaign"}})
        self.products = products_response.get("products", [])
        
        if self.products:
            table = Table(title="Available Media Products")
            table.add_column("Product ID", style="cyan")
            table.add_column("Name", style="green")
            table.add_column("Type", style="yellow")
            table.add_column("Price", style="magenta")
            
            for product in self.products:
                price = f"${product.get('cpm', 'Variable')} CPM" if product.get('is_fixed_price') else "Variable"
                table.add_row(
                    product.get('product_id', ''),
                    product.get('name', ''),
                    product.get('delivery_type', ''),
                    price
                )
            
            console.print(table)
            console.print(f"\n[green]✓ Found {len(self.products)} available products[/green]")
        else:
            console.print("[red]✗ No products available[/red]")
    
    async def _phase_2_buying(self):
        """Phase 2: Create the media buy."""
        console.print(Rule("[bold cyan]Phase 2: Media Buy Creation[/bold cyan]", style="cyan"))
        
        self._show_day(self.buy_date, "Executing media buy")
        
        # Create media buy
        buy_request = {
            "product_ids": ["prod_video_guaranteed_sports"],
            "flight_start_date": self.flight_start.isoformat(),
            "flight_end_date": self.flight_end.isoformat(),
            "total_budget": 50000.00,
            "targeting_overlay": {
                "geography": ["USA-CA", "USA-NY"],
                "content_categories_exclude": ["controversial", "politics"]
            },
            "po_number": f"PO-{self.principal_id.upper()}-{self.flight_start.year}-{self.flight_start.month:02d}"
        }
        
        console.print("\n[yellow]Creating media buy...[/yellow]")
        console.print(f"  • Products: Sports Video - Guaranteed")
        console.print(f"  • Budget: $50,000")
        console.print(f"  • Flight: {self.flight_start} to {self.flight_end}")
        console.print(f"  • Targeting: CA, NY (excluding controversial content)")
        
        buy_response = await self._call_tool("create_media_buy", {"req": buy_request})
        self.media_buy_id = buy_response.get("media_buy_id")
        
        if self.media_buy_id:
            console.print(f"\n[green]✓ Media buy created: {self.media_buy_id}[/green]")
        else:
            console.print("[red]✗ Failed to create media buy[/red]")
            console.print(f"[red]Response: {buy_response}[/red]")
            raise Exception("Media buy creation failed - cannot continue simulation")
    
    async def _phase_3_creatives(self):
        """Phase 3: Submit and monitor creative approval."""
        console.print(Rule("[bold cyan]Phase 3: Creative Submission & Approval[/bold cyan]", style="cyan"))
        
        self._show_day(self.creative_date, "Submitting creative assets")
        
        # Submit creatives
        creatives_request = {
            "media_buy_id": self.media_buy_id,
            "creatives": [
                {
                    "creative_id": "cr_purina_dog_30s_v1",
                    "format_id": "fmt_video_30s",
                    "content_uri": "https://cdn.purina.com/vast/dog_chow_30s_v1.xml"
                },
                {
                    "creative_id": "cr_purina_cat_30s_v1",
                    "format_id": "fmt_video_30s", 
                    "content_uri": "https://cdn.purina.com/vast/cat_chow_30s_v1.xml"
                }
            ]
        }
        
        console.print("\n[yellow]Submitting 2 video creatives for approval...[/yellow]")
        submit_response = await self._call_tool("submit_creatives", {"req": creatives_request})
        
        # Check initial status
        statuses = submit_response.get("statuses", [])
        for status in statuses:
            self.creative_ids.append(status.get("creative_id"))
            console.print(f"  • {status.get('creative_id')}: {status.get('status', 'unknown')}")
        
        # Simulate daily approval checks
        console.print("\n[yellow]Monitoring creative approval process...[/yellow]")
        
        approval_days = [
            self.creative_date + timedelta(days=1),
            self.creative_date + timedelta(days=2),
            self.creative_date + timedelta(days=3)
        ]
        
        for check_date in approval_days:
            self._show_day(check_date, "Checking creative approval status")
            
            status_response = await self._call_tool("check_creative_status", {
                "req": {"creative_ids": self.creative_ids}
            })
            
            all_approved = True
            for status in status_response.get("statuses", []):
                status_val = status.get("status", "unknown")
                emoji = "✓" if status_val == "approved" else "⏳"
                console.print(f"  {emoji} {status.get('creative_id')}: {status_val}")
                if status_val != "approved":
                    all_approved = False
            
            if all_approved:
                console.print("\n[green]✓ All creatives approved![/green]")
                break
    
    async def _phase_4_pre_flight(self):
        """Phase 4: Pre-flight checks and preparation."""
        console.print(Rule("[bold cyan]Phase 4: Pre-Flight Preparation[/bold cyan]", style="cyan"))
        
        # Check a few days before launch
        pre_flight_date = self.flight_start - timedelta(days=2)
        self._show_day(pre_flight_date, "Pre-flight system checks")
        
        console.print("\n[yellow]Verifying campaign setup...[/yellow]")
        
        # Get current delivery status (should show as scheduled)
        delivery_response = await self._call_tool("get_media_buy_delivery", {
            "req": {
                "media_buy_id": self.media_buy_id,
                "today": pre_flight_date.isoformat()
            }
        })
        
        status = delivery_response.get("status", "unknown")
        console.print(f"  • Campaign status: {status}")
        console.print(f"  • Days until launch: 2")
        console.print(f"  • Budget allocated: ${delivery_response.get('total_budget', 0):,.2f}")
        
        if status == "scheduled":
            console.print("\n[green]✓ Campaign ready for launch[/green]")
        else:
            console.print(f"\n[yellow]⚠️  Unexpected status: {status}[/yellow]")
    
    async def _phase_5_in_flight(self):
        """Phase 5: Monitor daily performance during flight."""
        console.print(Rule("[bold cyan]Phase 5: In-Flight Monitoring[/bold cyan]", style="cyan"))
        
        # Monitor key days during the flight
        monitoring_days = [
            (self.flight_start, "Campaign launch day"),
            (self.flight_start + timedelta(days=2), "Early performance check"),
            (self.flight_start + timedelta(days=5), "Mid-flight review"),
            (self.flight_start + timedelta(days=8), "Performance analysis")
        ]
        
        daily_data = []
        
        for check_date, description in monitoring_days:
            self._show_day(check_date, description)
            
            delivery_response = await self._call_tool("get_media_buy_delivery", {
                "req": {
                    "media_buy_id": self.media_buy_id,
                    "today": check_date.isoformat()
                }
            })
            
            # Store data for trend analysis
            daily_data.append({
                "date": check_date,
                "spend": delivery_response.get("spend", 0),
                "impressions": delivery_response.get("impressions", 0),
                "pacing": delivery_response.get("pacing", "unknown")
            })
            
            # Display current metrics
            days_elapsed = delivery_response.get("days_elapsed", 0)
            total_days = delivery_response.get("total_days", 0)
            progress = (days_elapsed / total_days * 100) if total_days > 0 else 0
            
            console.print(f"\n  📊 Day {days_elapsed} of {total_days} ({progress:.1f}% complete)")
            console.print(f"  💰 Spend: ${delivery_response.get('spend', 0):,.2f}")
            console.print(f"  👁️  Impressions: {delivery_response.get('impressions', 0):,}")
            console.print(f"  📈 Pacing: {delivery_response.get('pacing', 'unknown')}")
            
            # Calculate effective CPM
            if delivery_response.get('impressions', 0) > 0:
                ecpm = delivery_response.get('spend', 0) / delivery_response.get('impressions', 0) * 1000
                console.print(f"  💵 Effective CPM: ${ecpm:.2f}")
        
        # Show performance trend
        self._show_performance_trend(daily_data)
    
    def _show_performance_trend(self, daily_data: List[Dict]):
        """Display a simple performance trend visualization."""
        console.print("\n[bold yellow]Performance Trend:[/bold yellow]")
        
        max_impressions = max(d['impressions'] for d in daily_data) if daily_data else 1
        
        for data in daily_data:
            bar_length = int((data['impressions'] / max_impressions) * 40) if max_impressions > 0 else 0
            bar = "█" * bar_length
            
            console.print(
                f"{data['date'].strftime('%m/%d')}: {bar} "
                f"{data['impressions']:,} imps (${data['spend']:,.0f})"
            )
    
    async def _phase_6_optimization(self):
        """Phase 6: Mid-flight optimization."""
        console.print(Rule("[bold cyan]Phase 6: Mid-Flight Optimization[/bold cyan]", style="cyan"))
        
        optimization_date = self.flight_start + timedelta(days=7)
        self._show_day(optimization_date, "Optimization review")
        
        console.print("\n[yellow]Analyzing performance for optimization opportunities...[/yellow]")
        
        # Get current performance
        delivery_response = await self._call_tool("get_media_buy_delivery", {
            "req": {
                "media_buy_id": self.media_buy_id,
                "today": optimization_date.isoformat()
            }
        })
        
        # Send performance feedback to the ad server
        console.print("\n[yellow]Sending performance index feedback to ad server...[/yellow]")
        
        # Simulate different performance for the product
        # In reality, this would be based on actual business metrics
        performance_index = 1.2 if delivery_response.get("pacing") == "on_track" else 0.85
        
        performance_request = {
            "media_buy_id": self.media_buy_id,
            "performance_data": [
                {
                    "product_id": "prod_video_guaranteed_sports",
                    "performance_index": performance_index,
                    "confidence_score": 0.92
                }
            ]
        }
        
        perf_response = await self._call_tool("update_performance_index", {"req": performance_request})
        
        if perf_response.get("status") == "success":
            console.print(f"\n[green]✓ Performance index updated: {performance_index:.2f}[/green]")
        
        pacing = delivery_response.get("pacing", "unknown")
        
        if pacing == "under_delivery":
            console.print("\n[yellow]⚠️  Campaign under-delivering. Applying optimizations...[/yellow]")
            
            # Update targeting to expand reach
            update_request = {
                "media_buy_id": self.media_buy_id,
                "new_targeting_overlay": {
                    "geography": ["USA-CA", "USA-NY", "USA-TX", "USA-FL"],  # Add more states
                    "content_categories_exclude": ["controversial"]  # Reduce exclusions
                }
            }
            
            console.print("  • Expanding geographic targeting: +TX, +FL")
            console.print("  • Reducing content exclusions")
            
            update_response = await self._call_tool("update_media_buy", {"req": update_request})
            
            if update_response.get("status") == "success":
                console.print("\n[green]✓ Optimizations applied successfully[/green]")
            else:
                console.print("\n[red]✗ Failed to apply optimizations[/red]")
        
        elif pacing == "over_delivery":
            console.print("\n[yellow]📈 Campaign over-delivering. Consider increasing budget.[/yellow]")
        
        else:
            console.print("\n[green]✓ Campaign pacing on track. No optimization needed.[/green]")
    
    async def _phase_7_completion(self):
        """Phase 7: Campaign completion and final reporting."""
        console.print(Rule("[bold cyan]Phase 7: Campaign Completion[/bold cyan]", style="cyan"))
        
        # Check final day
        completion_date = self.flight_end + timedelta(days=1)
        self._show_day(completion_date, "Campaign completed - final report")
        
        final_response = await self._call_tool("get_media_buy_delivery", {
            "req": {
                "media_buy_id": self.media_buy_id,
                "today": completion_date.isoformat()
            }
        })
        
        # Display final results
        console.print("\n[bold green]📊 Final Campaign Report[/bold green]")
        console.print(Panel(
            f"[bold]Campaign ID:[/bold] {self.media_buy_id}\n"
            f"[bold]Status:[/bold] {final_response.get('status', 'unknown')}\n"
            f"[bold]Total Spend:[/bold] ${final_response.get('spend', 0):,.2f}\n"
            f"[bold]Total Impressions:[/bold] {final_response.get('impressions', 0):,}\n"
            f"[bold]Effective CPM:[/bold] ${final_response.get('spend', 0) / final_response.get('impressions', 0) * 1000:.2f}" if final_response.get('impressions', 0) > 0 else "",
            title="Campaign Summary",
            border_style="green"
        ))
        
        # Calculate delivery percentage
        budget = 50000.00
        delivery_pct = (final_response.get('spend', 0) / budget * 100) if budget > 0 else 0
        
        console.print(f"\n[bold]Budget Utilization:[/bold] {delivery_pct:.1f}%")
        
        if delivery_pct >= 95:
            console.print("[green]✓ Excellent delivery - budget fully utilized[/green]")
        elif delivery_pct >= 80:
            console.print("[yellow]✓ Good delivery - majority of budget utilized[/yellow]")
        else:
            console.print("[red]⚠️  Under-delivery - significant budget remaining[/red]")
        
        console.print("\n[bold magenta]🎉 Campaign lifecycle complete![/bold magenta]")
    
    async def _show_dry_run_logs(self):
        """Retrieve and display dry run logs if available."""
        try:
            logs_response = await self._call_tool("get_dry_run_logs", {})
            dry_run_logs = logs_response.get("dry_run_logs", [])
            
            if dry_run_logs:
                console.print(Rule("[bold yellow]Dry Run: Adapter Calls[/bold yellow]", style="yellow"))
                console.print("\n[dim]The following adapter calls would have been made:[/dim]\n")
                
                for log in dry_run_logs:
                    console.print(f"  [dim]{log}[/dim]")
                
                console.print(f"\n[bold yellow]Total adapter calls: {len(dry_run_logs)}[/bold yellow]")
        except Exception as e:
            # Dry run logs might not be available in all environments
            pass


async def main():
    """Run the full lifecycle simulation."""
    import sys
    
    # Get server URL from command line or use default
    server_url = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8000"
    
    # Run simulation for Purina
    sim = FullLifecycleSimulation(
        server_url=server_url,
        token=PURINA_TOKEN,
        principal_id="purina"
    )
    
    await sim.run()


if __name__ == "__main__":
    asyncio.run(main())
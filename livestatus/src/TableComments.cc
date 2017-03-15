// +------------------------------------------------------------------+
// |             ____ _               _        __  __ _  __           |
// |            / ___| |__   ___  ___| | __   |  \/  | |/ /           |
// |           | |   | '_ \ / _ \/ __| |/ /   | |\/| | ' /            |
// |           | |___| | | |  __/ (__|   <    | |  | | . \            |
// |            \____|_| |_|\___|\___|_|\_\___|_|  |_|_|\_\           |
// |                                                                  |
// | Copyright Mathias Kettner 2014             mk@mathias-kettner.de |
// +------------------------------------------------------------------+
//
// This file is part of Check_MK.
// The official homepage is at http://mathias-kettner.de/check_mk.
//
// check_mk is free software;  you can redistribute it and/or modify it
// under the  terms of the  GNU General Public License  as published by
// the Free Software Foundation in version 2.  check_mk is  distributed
// in the hope that it will be useful, but WITHOUT ANY WARRANTY;  with-
// out even the implied warranty of  MERCHANTABILITY  or  FITNESS FOR A
// PARTICULAR PURPOSE. See the  GNU General Public License for more de-
// tails. You should have  received  a copy of the  GNU  General Public
// License along with GNU Make; see the file  COPYING.  If  not,  write
// to the Free Software Foundation, Inc., 51 Franklin St,  Fifth Floor,
// Boston, MA 02110-1301 USA.

#include "TableComments.h"
#include <memory>
#include <utility>
#include "Column.h"
#include "DowntimeOrComment.h"
#include "DowntimesOrComments.h"  // IWYU pragma: keep
#include "OffsetBoolColumn.h"
#include "OffsetIntColumn.h"
#include "OffsetSStringColumn.h"
#include "OffsetTimeColumn.h"
#include "Query.h"
#include "TableHosts.h"
#include "TableServices.h"
#include "auth.h"

using std::make_unique;
using std::string;

// TODO(sp): the dynamic data in this table must be locked with a mutex

TableComments::TableComments(MonitoringCore *mc,
                             const DowntimesOrComments &downtimes_holder,
                             const DowntimesOrComments &comments_holder)
    : Table(mc), _holder(comments_holder) {
    addColumn(make_unique<OffsetSStringColumn>(
        "author", "The contact that entered the comment",
        DANGEROUS_OFFSETOF(Comment, _author_name), -1, -1, -1));
    addColumn(make_unique<OffsetSStringColumn>(
        "comment", "A comment text", DANGEROUS_OFFSETOF(Comment, _comment), -1,
        -1, -1));
    addColumn(make_unique<OffsetIntColumn>("id", "The id of the comment",
                                           DANGEROUS_OFFSETOF(Comment, _id), -1,
                                           -1, -1));
    addColumn(make_unique<OffsetTimeColumn>(
        "entry_time", "The time the entry was made as UNIX timestamp",
        DANGEROUS_OFFSETOF(Comment, _entry_time), -1, -1, -1));
    addColumn(make_unique<OffsetIntColumn>(
        "type", "The type of the comment: 1 is host, 2 is service",
        DANGEROUS_OFFSETOF(Comment, _type), -1, -1, -1));
    addColumn(make_unique<OffsetBoolColumn>(
        "is_service",
        "0, if this entry is for a host, 1 if it is for a service",
        DANGEROUS_OFFSETOF(Comment, _is_service), -1, -1, -1));

    addColumn(make_unique<OffsetIntColumn>(
        "persistent", "Whether this comment is persistent (0/1)",
        DANGEROUS_OFFSETOF(Comment, _persistent), -1, -1, -1));
    addColumn(make_unique<OffsetIntColumn>(
        "source", "The source of the comment (0 is internal and 1 is external)",
        DANGEROUS_OFFSETOF(Comment, _source), -1, -1, -1));
    addColumn(make_unique<OffsetIntColumn>(
        "entry_type",
        "The type of the comment: 1 is user, 2 is downtime, 3 is flap and 4 is acknowledgement",
        DANGEROUS_OFFSETOF(Comment, _entry_type), -1, -1, -1));
    addColumn(make_unique<OffsetIntColumn>(
        "expires", "Whether this comment expires",
        DANGEROUS_OFFSETOF(Comment, _expires), -1, -1, -1));
    addColumn(make_unique<OffsetTimeColumn>(
        "expire_time", "The time of expiry of this comment as a UNIX timestamp",
        DANGEROUS_OFFSETOF(Comment, _expire_time), -1, -1, -1));

    TableHosts::addColumns(this, mc, "host_",
                           DANGEROUS_OFFSETOF(Comment, _host), -1,
                           downtimes_holder, comments_holder);
    TableServices::addColumns(
        this, mc, "service_", DANGEROUS_OFFSETOF(Comment, _service),
        false /* no hosts table */, downtimes_holder, comments_holder);
}

string TableComments::name() const { return "comments"; }

string TableComments::namePrefix() const { return "comment_"; }

void TableComments::answerQuery(Query *query) {
    for (const auto &entry : _holder) {
        if (!query->processDataset(entry.second.get())) {
            break;
        }
    }
}

bool TableComments::isAuthorized(contact *ctc, void *data) {
    DowntimeOrComment *dtc = static_cast<DowntimeOrComment *>(data);
    return is_authorized_for(ctc, dtc->_host, dtc->_service);
}
